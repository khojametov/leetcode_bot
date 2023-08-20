from src.crud.base import BaseCRUDService
from src.crud.crud_statistics import StatisticsCRUDService
from src.crud.crud_users import UsersCRUDService
from src.crud.crud_link import LinksCRUDService
from src.models import User, Statistic, Link


user = UsersCRUDService(User)
statistic = StatisticsCRUDService(Statistic)
link = LinksCRUDService(Link)