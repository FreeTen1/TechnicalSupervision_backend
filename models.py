# update date: 2023-04-04 12:48
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime



class AsDictMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def as_dict(self):
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M')
            result[c.name] = value
        return result


Base = declarative_base(cls=AsDictMixin)
metadata = Base.metadata


class Artist(Base):
    __tablename__ = 'artists'
    __table_args__ = {'comment': 'Таблица Ф. И. О. осуществляющего технический надзор'}

    id = Column(INTEGER, primary_key=True, comment='id')
    fio = Column(String(255), nullable=False, comment='фио')


class Contractor(Base):
    __tablename__ = 'contractors'
    __table_args__ = {'comment': 'Таблица подрядчиков'}

    id = Column(INTEGER, primary_key=True, comment='id')
    name = Column(String(255), nullable=False, comment='Название сторонней организации (Подрядчик)')
    is_archived = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='Удалён ли подрядчик')


class DayType(Base):
    __tablename__ = 'day_types'
    __table_args__ = {'comment': 'Типы дней'}

    id = Column(INTEGER, primary_key=True)
    name = Column(String(255), nullable=False)


class PaidStatus(Base):
    __tablename__ = 'paid_statuses'
    __table_args__ = {'comment': 'Таблица статусов (оплачено, не оплачено)'}

    id = Column(INTEGER, primary_key=True)
    name = Column(String(255), nullable=False)


class ResponsibleDepartment(Base):
    __tablename__ = 'responsible_departments'
    __table_args__ = {'comment': 'Ответственное подразделение'}

    id = Column(INTEGER, primary_key=True)
    name = Column(String(255), nullable=False)


class StatusesExecution(Base):
    __tablename__ = 'statuses_execution'
    __table_args__ = {'comment': 'Таблица статусов выполнения (новая, в работе)'}

    id = Column(INTEGER, primary_key=True)
    name = Column(String(255), nullable=False)


class StatusesK(Base):
    __tablename__ = 'statuses_ks'
    __table_args__ = {'comment': 'таблица статусов кс'}

    id = Column(INTEGER, primary_key=True, comment='id')
    name = Column(String(255), nullable=False)


class Access(Base):
    __tablename__ = 'accesses'

    id = Column(INTEGER, primary_key=True)
    name = Column(String(255), nullable=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(INTEGER, primary_key=True)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    fio = Column(String(255), nullable=False)
    access_id = Column(ForeignKey('accesses.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True, server_default=text("'1'"))

    access = relationship('Access')

    def as_dict(self):
        result = super().as_dict()
        result.pop("password")
        result["access_name"] = self.access.name
        return result


class Supervision(Base):
    __tablename__ = 'supervisions'
    __table_args__ = {'comment': 'Основная таблица технического надзора'}

    id = Column(INTEGER, primary_key=True, comment='id записи')
    datetime_start = Column(DateTime, nullable=False, comment='Дата, время начала работ')
    datetime_end = Column(DateTime, nullable=False, comment='Дата, время окончания работ')
    day_type_id = Column(ForeignKey('day_types.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True, comment='тип дня')
    station = Column(Text, comment='Станция (место проведения работ)')
    department_responsible_id = Column(ForeignKey('responsible_departments.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True, server_default=text("'1'"), comment='Ответственное подразделение (отдел)')
    department_distance = Column(String(255), comment='Отдел, Дистанция')
    artist_id = Column(ForeignKey('artists.id', ondelete='RESTRICT', onupdate='CASCADE'), index=True, comment='Ф. И. О. осуществляющего технический надзор')
    type_work = Column(Text, comment='Вид проводимой работы (объем произведенной работы)')
    contractor_id = Column(ForeignKey('contractors.id', ondelete='RESTRICT', onupdate='CASCADE'), index=True, comment='Название сторонней организации (Подрядчик)')
    manufacturer_info = Column(String(255), comment='Фамилия, Имя, телефон производителя')
    order_number = Column(String(255), comment='Номер совместного приказа')
    note = Column(Text, comment='Примечание')
    status_ks_id = Column(ForeignKey('statuses_ks.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True, server_default=text("'2'"), comment='Статус КС')
    comment = Column(String(255), comment='Поле комментария, если учтено в КС')
    paid_status_id = Column(ForeignKey('paid_statuses.id', ondelete='RESTRICT', onupdate='CASCADE'), index=True, comment='Оплачено')
    amount = Column(INTEGER, comment='Сумма, руб.')
    status_execution_id = Column(ForeignKey('statuses_execution.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True, server_default=text("'1'"), comment='Статус выполнения (выполнена, в работе)')
    is_archived = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='удалена ли строка')

    artist = relationship('Artist')
    contractor = relationship('Contractor')
    day_type = relationship('DayType')
    department_responsible = relationship('ResponsibleDepartment')
    paid_status = relationship('PaidStatus')
    status_execution = relationship('StatusesExecution')
    status_ks = relationship('StatusesK')

    def as_dict(self):
        result = super().as_dict()
        result["artist"] = self.artist.fio if self.artist else None
        result["contractor"] = self.contractor.name if self.contractor else None
        result["day_type"] = self.day_type.name if self.day_type else None
        result["department_responsible"] = self.department_responsible.name if self.department_responsible else None
        result["paid_status"] = self.paid_status.name if self.paid_status else None
        result["status_execution"] = self.status_execution.name if self.status_execution else None
        result["status_ks"] = self.status_ks.name if self.status_ks else None
        
        return result
