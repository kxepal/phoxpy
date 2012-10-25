# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.mapping import (
    BooleanField, DateTimeField, IntegerField, ListField, LongField, Mapping,
    ObjectField, RefField, TextField
)
from phoxpy.messages import PhoxRequestContent


class RegistrationJournalFilter(Mapping):
    bill_number = TextField(name='billNr')
    billed = IntegerField(default=2)
    copy_sent = IntegerField(name='copySent', default=2)
    custom_departments = ListField(RefField(), name='custDepartments')
    custom_states = ListField(RefField(), name='customStates')
    date_from = DateTimeField(name='dateFrom')
    date_till = DateTimeField(name='dateTill')
    defect_state = IntegerField(name='defectState', default=0)
    delivered = IntegerField(default=2)
    departments = ObjectField(Mapping.build(
        operator=TextField(default='OR'),
        id_list=ListField(RefField(), name='idList'),
    ))
    doctors = ListField(RefField())
    empty_pay_category = BooleanField(name='emptyPayCategory', default=False)
    first_name = TextField(name='firstName')
    hospitals = ListField(RefField())
    nr = TextField()
    last_name = TextField(name='lastName')
    last_timestamp = LongField(name='lastTimestamp', default=0)
    mark_plan_deviation = BooleanField(name='markPlanDeviation', default=False)
    middle_name = TextField(name='middleName')
    only_delayed = BooleanField(name='onlyDelayed', default=False)
    original_sent = IntegerField(name='originalSent', default=2)
    patient_codes = ListField(RefField(), name='patientCodes')
    patient_present = IntegerField(name='patientPresent', default=2)
    patient_nr = TextField(name='patientNr')
    pay_categories = ListField(RefField(), name='payCategories')
    printed = IntegerField(default=2)
    priority = IntegerField(default=0)
    request_nr = TextField(name='nr')
    request_forms = ListField(RefField(), name='requestForms')
    sex = IntegerField(default=3)
    states = ListField(RefField())
    targets = ObjectField(Mapping.build(
        operator=TextField(default='OR'),
        id_list=ListField(RefField(), name='idList'),
    ))


class RegistrationJournalRequest(PhoxRequestContent):
    filter = ObjectField(RegistrationJournalFilter)
