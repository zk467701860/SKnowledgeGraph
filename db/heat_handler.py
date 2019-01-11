# _*_ coding: utf-8 _*_
from pymysql import OperationalError

from db.engine_factory import EngineFactory
from db.model import EntityHeat


class SQLHeatHandler():
    def __init__(self, session=None, logger=None):
        self.session = session
        self.logger = logger

    def get_session(self):
        if not self.session:
            self.session = EngineFactory.create_session()

        return self.session

    def like(self, api_id):
        try:
            session = self.get_session()
            now_heat = 1
            result = session.execute("SELECT * FROM api_heat WHERE api_id=:param", {"param": api_id}).first()
            if result is None:
                session.execute("insert into codehub.api_heat(api_heat.heat,api_heat.api_id) value(:param1,:param2)",
                                {"param1": 1, "param2": api_id})
            else:
                now_heat = result['heat']
                now_heat += 1
                result_id = result['id']
                session.execute("UPDATE codehub.api_heat SET heat =:param1 WHERE (id =:param2)",
                                {"param1": now_heat, "param2": result_id})

            return {'heat': now_heat}
        except Exception:
            self.session = None
            if self.logger:
                self.logger.exception("exception occur in api_id=%s", api_id)

            return {'heat': 0}

    def get_api_heat_by_apiID(self, api_id):
        try:
            session = self.get_session()
            result = session.execute("SELECT * FROM api_heat WHERE api_id=:param", {"param": api_id}).first()
            if result is not None:
                r = {
                    "id": result['id'],
                    "heat": result['heat'],
                    'api_id': result['api_id']
                }
                return r

        except OperationalError:
            self.session = None
            if self.logger:
                self.logger.exception("exception occur in api_id=%s", api_id)
        except Exception:
            self.session = None
            if self.logger:
                self.logger.exception("exception occur in api_id=%s", api_id)
        return {
            "id": -1,
            "heat": 0,
            'api_id': -1
        }

    def get_most_popular_entity_id_list(self, top_number=10):
        try:
            session = self.get_session()
            team_result = session.query(EntityHeat).order_by(EntityHeat.heat.desc()).limit(top_number).all()
            if team_result is None:
                return []

            result_list = []
            for entity in team_result:
                result_list.append({
                    "id": entity.id,
                    "heat": entity.heat,
                    'api_id': entity.api_id
                })
            return result_list
        except Exception:
            if self.logger:
                self.logger.exception("exception occur in get_most_popular_entity_id_list()")
            self.session = None
            return []
