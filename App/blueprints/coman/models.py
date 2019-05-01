import datetime
import string
from collections import OrderedDict

import pytz
from sqlalchemy import and_, or_, text

from sqlalchemy.ext.hybrid import hybrid_property

from lib.util_sqlalchemy import ResourceMixin, AwareDateTime
from App.extensions import db


class Coman(ResourceMixin, db.Model):

    __tablename__ = 'comans'
    id = db.Column(db.Integer, primary_key=True)

    # Coupon details.
    name = db.Column(db.String(128), index=True, unique=True)
    address = db.Column(db.String(255))
    city = db.Column(db.String(128), index=True)
    state = db.Column(db.String(2))
    zip = db.Column(db.Integer())
    contact = db.Column(db.String(128))
    contactPosition = db.Column(db.String(1128))
    cellphone = db.Column(db.String(128))
    directphone = db.Column(db.String(128))
    email = db.Column(db.String(255))
    website = db.Column(db.String(128))
    notes = db.Column(db.String())
    nda = db.Column(db.Boolean(), index=True)

    capabilities = db.Column(db.String(255))
    knowncustomers = db.Column(db.String(255))
    equipment = db.Column(db.String(255))

    minOrderQtd = db.Column(db.Integer())
    batchsize = db.Column(db.Integer())
    maxcapacity = db.Column(db.Float(), default=0)

    allergensRunLine = db.Column(db.String(255))
    allergensProhbLine = db.Column(db.String(255))

    allergensRunPlant = db.Column(db.String(255))
    allergensProhbPlant = db.Column(db.String(255))

    gfsi = db.Column(db.Boolean(), index=True)
    nameOfAllThemGFSI = db.Column(db.String(255))

    organic = db.Column(db.Boolean(), index=True)
    nameOfAllThemOrganic = db.Column(db.String(255))

    kosherCert = db.Column(db.Boolean(), index=True)
    nameOfAllThemKosherCert = db.Column(db.String(255))

    halalCert = db.Column(db.Boolean(), index=True)
    nameOfAllThemHalalCert = db.Column(db.String(255))

    gmoCert = db.Column(db.Boolean(), index=True)
    nameOfAllThemGMOCert = db.Column(db.String(255))

    usadInspect = db.Column(db.Boolean(), index=True)
    otherInspecAudits = db.Column(db.String(255))

    glutenFreeCert = db.Column(db.Boolean(), index=True)
    nameOfAllThemGlutenFreeCert = db.Column(db.String(255))

    otherCert = db.Column(db.String())
    realChocolate = db.Column(db.Boolean(), index=True)

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if query == '':
            return text('')

        search_query = '%{0}%'.format(query)

        return or_(Coman.name.ilike(search_query), Coman.city.ilike(search_query),
                    Coman.contact.ilike(search_query))

