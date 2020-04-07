import pytest
import unittest
import sys
from random import randint
from datetime import datetime


from flask import Flask

sys.path.append(".")


from flask_sqlalchemy import SQLAlchemy
from app.main.models.ai_model import Model, ModelCheckPoint
from app.main.syft_assets.protocol import Protocol
from app.main.syft_assets.plan import Plan
from app.main.workers.worker import Worker
from app.main.cycles.worker_cycle import WorkerCycle
from app.main.processes.fl_process import FLProcess
from app.main.cycles.cycle import Cycle
from app.main.processes.config import Config
from app.main import db

app = Flask(__name__)

BIG_INT = 2 ** 32


class TestDatabase(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        self.db = db
        self.db.init_app(app)
        app.app_context().push()
        self.db.create_all()

    def testCreatePlan(self):
        my_plan = Plan(
            id=randint(0, BIG_INT),
            value="list of plan values".encode("utf-8"),
            value_ts="torchscript(plan)".encode("utf-8"),
        )
        self.db.session.add(my_plan)
        self.db.session.commit()

    def testCreateProtocol(self):
        my_protocol = Protocol(
            id=randint(0, BIG_INT),
            value="list of protocol values".encode("utf-8"),
            value_ts="torchscript(protocol)".encode("utf-8"),
        )
        self.db.session.add(my_protocol)
        self.db.session.commit()

    def testCreateConfig(self):
        client_config = {
            "name": "my-federated-model",
            "version": "0.1.0",
            "batch_size": 32,
            "lr": 0.01,
            "optimizer": "SGD",
        }

        server_config = {
            "max_workers": 100,
            "pool_selection": "random",  # or "iterate"
            "num_cycles": 5,
            "do_not_reuse_workers_until_cycle": 4,
            "cycle_length": 8 * 60 * 60,  # 8 hours
            "minimum_upload_speed": 2000,  # 2 mbps
            "minimum_download_speed": 4000,  # 4 mbps
        }

        my_server_config = Config(id=randint(0, BIG_INT), config=server_config)

        my_client_config = Config(id=randint(0, BIG_INT), config=client_config)

        self.db.session.add(my_server_config)
        self.db.session.add(my_client_config)
        self.db.session.commit()

    def testCreateWorker(self):
        worker = Worker(
            id=randint(0, BIG_INT),
            format_preference="list",
            ping=randint(0, 100),
            avg_download=randint(0, 100),
            avg_upload=randint(0, 100),
        )

        self.db.session.add(worker)
        self.db.session.commit()

    def testCreateCycle(self):
        new_cycle = Cycle(
            id=randint(0, BIG_INT),
            start=datetime(2019, 2, 21, 7, 29, 32, 45),
            sequence=randint(0, 100),
            end=datetime(2019, 2, 22, 7, 29, 32, 45),
        )

        self.db.session.add(new_cycle)
        self.db.session.commit()

    def testCreateModel(self):
        new_model = Model(version="0.0.1")

        self.db.session.add(new_model)
        self.db.session.commit()

    def testCreateFLProcess(self):
        new_fl_process = FLProcess(id=randint(0, BIG_INT))

        self.db.session.add(new_fl_process)

        new_model = Model(version="0.0.1", flprocess=new_fl_process)

        self.db.session.add(new_model)

        avg_plan = Plan(
            id=randint(0, BIG_INT),
            value="list of plan values".encode("utf-8"),
            value_ts="torchscript(plan)".encode("utf-8"),
            avg_flprocess=new_fl_process,
        )

        self.db.session.add(avg_plan)

        training_plan = Plan(
            id=randint(0, BIG_INT),
            value="list of plan values".encode("utf-8"),
            value_ts="torchscript(plan)".encode("utf-8"),
            plan_flprocess=new_fl_process,
        )

        self.db.session.add(training_plan)

        validation_plan = Plan(
            id=randint(0, BIG_INT),
            value="list of plan values".encode("utf-8"),
            value_ts="torchscript(plan)".encode("utf-8"),
            plan_flprocess=new_fl_process,
        )

        self.db.session.add(validation_plan)

        protocol_1 = Protocol(
            id=randint(0, BIG_INT),
            value="list of protocol values".encode("utf-8"),
            value_ts="torchscript(protocol)".encode("utf-8"),
            protocol_flprocess=new_fl_process,
        )

        self.db.session.add(protocol_1)

        protocol_2 = Protocol(
            id=randint(0, BIG_INT),
            value="list of protocol values".encode("utf-8"),
            value_ts="torchscript(protocol)".encode("utf-8"),
            protocol_flprocess=new_fl_process,
        )

        self.db.session.add(protocol_2)

        client_config = {
            "name": "my-federated-model",
            "version": "0.1.0",
            "batch_size": 32,
            "lr": 0.01,
            "optimizer": "SGD",
        }

        server_config = {
            "max_workers": 100,
            "pool_selection": "random",  # or "iterate"
            "num_cycles": 5,
            "do_not_reuse_workers_until_cycle": 4,
            "cycle_length": 8 * 60 * 60,  # 8 hours
            "minimum_upload_speed": 2000,  # 2 mbps
            "minimum_download_speed": 4000,  # 4 mbps
        }

        server_config = Config(
            id=randint(0, BIG_INT),
            config=server_config,
            server_flprocess_config=new_fl_process,
        )

        client_config = Config(
            id=randint(0, BIG_INT),
            config=client_config,
            client_flprocess_config=new_fl_process,
        )

        self.db.session.add(client_config)
        self.db.session.add(server_config)

        cycle_1 = Cycle(
            id=randint(0, BIG_INT),
            start=datetime(2019, 2, 21, 7, 29, 32, 45),
            sequence=randint(0, 100),
            end=datetime(2019, 2, 22, 7, 29, 32, 45),
            cycle_flprocess=new_fl_process,
        )

        cycle_2 = Cycle(
            id=randint(0, BIG_INT),
            start=datetime(2019, 2, 27, 15, 19, 22),
            sequence=randint(0, 100),
            end=datetime(2019, 2, 28, 15, 19, 22),
            cycle_flprocess=new_fl_process,
        )

        self.db.session.add(cycle_1)
        self.db.session.add(cycle_2)
        self.db.session.commit()

    def testWorkerCycle(self):
        new_fl_process = FLProcess(id=randint(0, BIG_INT))

        self.db.session.add(new_fl_process)

        new_model = Model(version="0.0.1", flprocess=new_fl_process)

        self.db.session.add(new_model)

        avg_plan = Plan(
            id=randint(0, BIG_INT),
            value="list of plan values".encode("utf-8"),
            value_ts="torchscript(plan)".encode("utf-8"),
            avg_flprocess=new_fl_process,
        )

        self.db.session.add(avg_plan)

        training_plan = Plan(
            id=randint(0, BIG_INT),
            value="list of plan values".encode("utf-8"),
            value_ts="torchscript(plan)".encode("utf-8"),
            plan_flprocess=new_fl_process,
        )

        self.db.session.add(training_plan)

        validation_plan = Plan(
            id=randint(0, BIG_INT),
            value="list of plan values".encode("utf-8"),
            value_ts="torchscript(plan)".encode("utf-8"),
            plan_flprocess=new_fl_process,
        )

        self.db.session.add(validation_plan)

        protocol = Protocol(
            id=randint(0, BIG_INT),
            value="list of protocol values".encode("utf-8"),
            value_ts="torchscript(protocol)".encode("utf-8"),
            protocol_flprocess=new_fl_process,
        )

        self.db.session.add(protocol)

        client_config = {
            "name": "my-federated-model",
            "version": "0.1.0",
            "batch_size": 32,
            "lr": 0.01,
            "optimizer": "SGD",
        }

        server_config = {
            "max_workers": 100,
            "pool_selection": "random",  # or "iterate"
            "num_cycles": 5,
            "do_not_reuse_workers_until_cycle": 4,
            "cycle_length": 8 * 60 * 60,  # 8 hours
            "minimum_upload_speed": 2000,  # 2 mbps
            "minimum_download_speed": 4000,  # 4 mbps
            "model_name": "testy_mcTeserson",  # @TODO: @IonesioJunior @cereallarceny: do we add this value here as well or do we have a foreignkey look up to the server_config? see this for more detaisl https://github.com/OpenMined/Roadmap/blob/master/web_and_mobile_team/projects/federated_learning.md 2. test and 3. host
            "JWT_VERIFY_API": "google.com",
            "JWT_with_RSA": True,
            "JWT_PUB_KEY": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDAswWWr/kU9Z5kj7KIQEs54B9x1MaEhEp4WDZPJ+PGONfg2tD4BKuGtDl345f4zgx7EPZL7EZRApLq6HxcznVbLleIbyqKkzvR88zHLBaxQ9GBRx+0kH8VqZspmMI/6fDBVm/SDtG1GOAYPwX1zK3DZZFMkkA2v8oGZ3U791jd9gy7S5CxewJrFMcFMStj9x8x3tW07OAdC7/HZpa5zKE2rWN01tytxbsl9/coMNBAfWIWEflhZgRz2+Onp2uDaXez7RNTe4m0+tQlx2FD0Pb7rFvlKwsgziKBReO8wwCQXWqcAPLsIXCOfUZXlBNpvPvp9I4HPEffaHyR1FC2eRoj4hzUibEu0+OQNj7QM5P9KsMV9k4wxURFxsd78rlFF8cnbKwIMf5nB8/FbqL/IyJOggxtntHr1Gum44QnG794GtSQHZNlWKKak2z/u2O++flxfZ9dBBAYWjJYM5kIT+X9NVYbWWryBqupHYipwP8f3vovKWVacOMMm3S0z76O5IDiIp5Gjnsifbnz57FWQok0HrSv8l3QMRPCxi3SjIFyI2ZusFC/4VLy9zZXQe07qI6l7s91UN6W8VW1YUFQ7nLGffkpAd/bLZSOueYQrf5tslQjZf3Jon5C/MkTJ7PGyOUmoAYya2kyKi4izMg/ODRIloVbWjU6tEPWyhzK8VMsXw== root@388da63cf68e",
            "JWT_SECRET": "very long a$$ very secret key phrase",
        }

        server_config = Config(
            id=randint(0, BIG_INT),
            config=server_config,
            server_flprocess_config=new_fl_process,
        )

        client_config = Config(
            id=randint(0, BIG_INT),
            config=client_config,
            client_flprocess_config=new_fl_process,
        )

        self.db.session.add(client_config)
        self.db.session.add(server_config)

        cycle = Cycle(
            id=randint(0, BIG_INT),
            start=datetime(2019, 2, 21, 7, 29, 32, 45),
            sequence=randint(0, 100),
            end=datetime(2019, 2, 22, 7, 29, 32, 45),
            cycle_flprocess=new_fl_process,
        )

        self.db.session.add(cycle)

        worker = Worker(
            id=randint(0, BIG_INT),
            format_preference="list",
            ping=randint(0, 100),
            avg_download=randint(0, 100),
            avg_upload=randint(0, 100),
        )

        self.db.session.add(worker)

        worker_cycle = WorkerCycle(
            id=randint(0, BIG_INT),
            request_key="long_hashcode_here",
            worker=worker,
            cycle=cycle,
        )

        self.db.session.add(worker_cycle)
        self.db.session.commit()

        """auth test cases:

           "/federated/authenticate"
           params refers to values in server_config
           to generate test cases/assets: colab notebook => https://colab.research.google.com/drive/1HS86sFLvxi-AoeJHUIyonSkM-CkdOh9d

        1. HIGH_SECURITY_RISK_NO_AUTH_FLOW = True
            params: JWT_VERIFY_API = None
            API call: do not need to include `auth_token`
            expect: returns {status: success, worker_id: xxxx}

        2. HIGH_SECURITY_RISK_NO_AUTH_FLOW = False, but no auth_token
            params: JWT_VERIFY_API = not None
            API call: no `auth_token'
            expects: returns {"error": "Authentication is required, please pass an 'auth_token'."}

        3. HIGH_SECURITY_RISK_NO_AUTH_FLOW = False, RSA verification fails
            params: JWT_VERIFY_API = not None, RSA = True
            API call: {auth_token: something_encrypted_with_different_private_key} (see colab notebook)
            expect: returns {"error": "The 'auth_token' you sent is invalid."}

        4. HIGH_SECURITY_RISK_NO_AUTH_FLOW = False, RSA verification succeeds
            params: JWT_VERIFY_API = not None, RSA = True
            API call: {auth_token: wisomething_encrypted_with_correct_key} (see colab notebook)
            expect: same as 1.

        5. HIGH_SECURITY_RISK_NO_AUTH_FLOW = False, HSA verification fails
            params: JWT_VERIFY_API = not None, RSA = False
            API call: {auth_token: wisomething_encrypted_with_different_secretPhrase} (see colab notebook)
            expect: same as 3

        6. HIGH_SECURITY_RISK_NO_AUTH_FLOW = False, HSA verification succeeds
            params: JWT_VERIFY_API = not None, RSA = False
            API call: {auth_token: wisomething_encrypted_with_correct_secretPhrase} (see colab notebook)
            expect: same as 1

        7. 3rd_part_verification fails
            params: JWT_VERIFY_API = not None, RSA = False
            API call: same as 6
            Other_step: change line 324 in app/routes/fedreated.py to .post
            expect: return {"error": "The 'auth_token' you sent did not pass 3rd party verificaiton."}

        """
