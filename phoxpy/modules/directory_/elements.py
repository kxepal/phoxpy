# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.mapping import (
    Mapping,
    BooleanField, DateTimeField, FloatField, IntegerField, ListField, LongField,
    ObjectField, RefField, TextField
)
from phoxpy.modules.directory_.base import (
    BaseDirectoryItem, DirectoryItem, RemovableMixIn, DirectoryGroupsMixIn,
    MnemonicsMixIn
)


################################################################################


class AccessRight(BaseDirectoryItem):
    groups = ListField(RefField(), name='groups')

    @property
    def directory(self):
        return 'accessRight'


################################################################################


class Antibiotic(DirectoryItem):
    pass

    @property
    def directory(self):
        return 'antibiotic'


################################################################################


class BioMaterial(DirectoryItem):
    defect_types = ListField(RefField(), name='defectTypes')
    eng_name = TextField(name='engName')
    targets = ListField(RefField(), name='targets')

    @property
    def directory(self):
        return 'bioMaterial'


################################################################################


class CategoryFactor(Mapping):
    category = RefField(name='category')
    id = IntegerField(name='id')
    materials = ListField(RefField(), name='materials')
    name = TextField(name='name')


class Category(DirectoryItem):
    factors = ListField(ObjectField(CategoryFactor), name='factors')

    @property
    def directory(self):
        return 'category'


################################################################################


class CommentSource(DirectoryItem):
    begin_line = BooleanField(name='beginLine')
    departments = ListField(RefField(), name='departments')
    end_line = BooleanField(name='endLine')

    @property
    def directory(self):
        return 'commentSource'


################################################################################


class CustDepartment(BaseDirectoryItem, RemovableMixIn, MnemonicsMixIn):
    doctors = ListField(TextField(), name='doctors')
    eng_name = TextField(name='engName')
    hospital = RefField(name='hospital')

    @property
    def directory(self):
        return 'custDepartment'


################################################################################


class Command(Mapping):
    command_type = IntegerField(name='commandType')
    custom_report = RefField(name='customReport')
    group_name = TextField(name='groupName')
    id = IntegerField(name='id')


class CustomCommand(BaseDirectoryItem, DirectoryGroupsMixIn):
    commands = ListField(ObjectField(Command), name='commands')
    journal_ref_id = IntegerField(name='journalRefId')
    journal_type = IntegerField(name='journalType')

    @property
    def directory(self):
        return 'customCommand'


################################################################################


class DataSource(Mapping):
    code = TextField(name='code')
    description = TextField(name='description')
    id = IntegerField(name='id')
    mnemonics = TextField(name='mnemonics')
    name = TextField(name='name')
    sql = TextField(name='sql')
    sql_bytes = TextField(name='sqlBytes')


class Parameter(Mapping):
    allow_empty = BooleanField(name='allowEmpty')
    category = RefField(name='category')
    code = TextField(name='code')
    default_value = TextField(name='defaultValue')
    description = TextField(name='description')
    display_expression = TextField(name='displayExpression')
    group_name = TextField(name='groupName')
    id = IntegerField(name='id')
    name = TextField(name='name')
    parameter_type = IntegerField(name='parameterType')
    rank = IntegerField(name='rank')
    start_group = BooleanField(name='startGroup')
    system_dictionary = BooleanField(name='systemDictionary')
    system_dictionary_code = TextField(name='systemDictionaryCode')
    time_mode = IntegerField(name='timeMode')
    update_prices_mode = IntegerField(name='updatePricesMode')


class CustomReport(DirectoryItem):
    data_sources = ListField(ObjectField(DataSource), name='dataSources')
    description = TextField(name='description')
    parameters = ListField(ObjectField(Parameter), name='parameters')
    print_form_template = TextField(name='printFormTemplate')
    print_form_template_bytes = TextField(name='printFormTemplateBytes')
    user_groups = ListField(RefField(), name='userGroups')

    @property
    def directory(self):
        return 'customReport'

################################################################################


class DefectType(DirectoryItem):
    all_biomaterials = BooleanField(name='allBiomaterials')
    biomaterials = ListField(TextField(), name='biomaterials')
    skip_service = BooleanField(name='skipService')
    tests = ListField(RefField(), name='tests')
    work_comment = TextField(name='workComment')

    @property
    def directory(self):
        return 'defectType'


################################################################################


class Department(DirectoryItem):
    all_batch_worklists = BooleanField(name='allBatchWorklists')
    allow_department_nr = BooleanField(name='allowDepartmentNr')
    batch_worklists = ListField(TextField(), name='batchWorklists')
    default_norm_high_comment = TextField(name='defaultNormHighComment')
    default_norm_high_critical_comment = TextField(name='defaultNormHighCriticalComment')
    default_norm_low_comment = TextField(name='defaultNormLowComment')
    default_norm_low_critical_comment = TextField(name='defaultNormLowCriticalComment')
    default_norm_normal_comment = TextField(name='defaultNormNormalComment')
    department_nr_period = IntegerField(name='departmentNrPeriod')
    external_nr_offset = IntegerField(name='externalNrOffset')
    external_nr_template = TextField(name='externalNrTemplate')
    laboratory = RefField(name='laboratory')
    layout = RefField(name='layout')
    micro = BooleanField(name='micro')
    print_forms = ListField(RefField(), name='printForms')
    publish_report_on_request_approve = BooleanField(name='publishReportOnRequestApprove')
    publish_report_on_request_cancel = BooleanField(name='publishReportOnRequestCancel')
    publish_report_on_result_approve = BooleanField(name='publishReportOnResultApprove')
    publish_report_on_result_cancel = BooleanField(name='publishReportOnResultCancel')
    request_approve_report_name_template = TextField(name='requestApproveReportNameTemplate')
    request_cancel_report_name_template = TextField(name='requestCancelReportNameTemplate')
    result_approve_print_forms = ListField(TextField(), name='resultApprovePrintForms')
    result_approve_report_name_template = TextField(name='resultApproveReportNameTemplate')
    result_cancel_print_forms = ListField(TextField(), name='resultCancelPrintForms')
    result_cancel_report_name_template = TextField(name='resultCancelReportNameTemplate')
    skip_show_in_process_view = BooleanField(name='skipShowInProcessView')
    use_external_nr = BooleanField(name='useExternalNr')
    use_myelogram = BooleanField(name='useMyelogram')
    use_sample_journal = BooleanField(name='useSampleJournal')

    @property
    def directory(self):
        return 'department'


################################################################################


class Doctor(BaseDirectoryItem, MnemonicsMixIn, RemovableMixIn):
    cust_department = RefField(name='custDepartment')
    description = TextField(name='description')
    eng_name = TextField(name='engName')

    @property
    def directory(self):
        return 'doctor'


################################################################################


class Employee(DirectoryItem):
    abbr_name_with_title = TextField(name='abbrNameWithTitle')
    degree = TextField(name='degree')
    departments = ListField(RefField(), name='departments')
    eng_abbr_name_with_title = TextField(name='engAbbrNameWithTitle')
    eng_degree = TextField(name='engDegree')
    eng_first_name = TextField(name='engFirstName')
    eng_full_name = TextField(name='engFullName')
    eng_last_name = TextField(name='engLastName')
    eng_middle_name = TextField(name='engMiddleName')
    eng_profession = TextField(name='engProfession')
    first_name = TextField(name='firstName')
    full_name = TextField(name='fullName')
    hospitals = ListField(TextField(), name='hospitals')
    last_name = TextField(name='lastName')
    login = TextField(name='login')
    middle_name = TextField(name='middleName')
    password = TextField(name='password')
    print_form_graphics = ListField(TextField(), name='printFormGraphics')
    print_form_strings = ListField(TextField(), name='printFormStrings')
    profession = TextField(name='profession')
    reports = ListField(RefField(), name='reports')
    title = TextField(name='title')
    user_groups = ListField(RefField(), name='userGroups')

    @property
    def directory(self):
        return 'employee'


################################################################################


class TestMapping(Mapping):
    code = TextField(name='code')
    equipment = RefField(name='equipment')
    id = IntegerField(name='id')
    qc_test_code = TextField(name='qcTestCode')
    test = RefField(name='test')


class Equipment(DirectoryItem):
    allow_lot_nr = BooleanField(name='allowLotNr')
    allow_work_journal = BooleanField(name='allowWorkJournal')
    allow_work_lists = BooleanField(name='allowWorkLists')
    auto_change_work_state_on_query = BooleanField(name='autoChangeWorkStateOnQuery')
    auto_work_add = BooleanField(name='autoWorkAdd')
    biomaterials = ListField(RefField(), name='biomaterials')
    departments = ListField(RefField(), name='departments')
    driver_id = TextField(name='driverId')
    driver_settings = TextField(name='driverSettings')
    lot_count = IntegerField(name='lotCount')
    lot_numering_type = IntegerField(name='lotNumeringType')
    need_reverse_process = BooleanField(name='needReverseProcess')
    old_driver = BooleanField(name='oldDriver')
    pipetted_racks = ListField(TextField(), name='pipettedRacks')
    position_count = IntegerField(name='positionCount')
    position_numering_type = IntegerField(name='positionNumeringType')
    query_mode = IntegerField(name='queryMode')
    request_form = RefField(name='requestForm')
    results_mode = IntegerField(name='resultsMode')
    save_algorithm = IntegerField(name='saveAlgorithm')
    send_position_as_coordinates = BooleanField(name='sendPositionAsCoordinates')
    skip_show_in_process_view = BooleanField(name='skipShowInProcessView')
    test_mappings = ListField(ObjectField(TestMapping), name='testMappings')

    @property
    def directory(self):
        return 'equipment'


################################################################################


class EquipmentTestGroups(DirectoryItem):
    active_test = RefField(name='activeTest')
    department = RefField(name='department')
    tests = ListField(RefField(), name='tests')

    @property
    def directory(self):
        return 'equipmentTestGroups'


################################################################################


class ExternalSystem(DirectoryItem):
    active = BooleanField(name='active')
    approve_received_works = BooleanField(name='approveReceivedWorks')
    cancel_received_works = BooleanField(name='cancelReceivedWorks')
    connection_string = TextField(name='connectionString')
    events = ListField(TextField(), name='events')
    export_all_works = BooleanField(name='exportAllWorks')
    external_type = IntegerField(name='externalType')
    hospital = RefField(name='hospital')
    hospitals = ListField(TextField(), name='hospitals')
    info_scan_form = RefField(name='infoScanForm')
    line_break_interval = IntegerField(name='lineBreakInterval')
    lock_requests_on_close = BooleanField(name='lockRequestsOnClose')
    lock_requests_on_create = BooleanField(name='lockRequestsOnCreate')
    poll_results_inc_day = IntegerField(name='pollResultsIncDay')
    poll_results_interval = IntegerField(name='pollResultsInterval')
    poll_results_time = DateTimeField(name='pollResultsTime')
    receive_queue_interval = IntegerField(name='receiveQueueInterval')
    registration_inc_day = IntegerField(name='registrationIncDay')
    registration_time = DateTimeField(name='registrationTime')
    scan_forms = ListField(RefField(), name='scanForms')
    send_only_approved_works = BooleanField(name='sendOnlyApprovedWorks')
    send_only_closed_requests = BooleanField(name='sendOnlyClosedRequests')
    send_only_closed_samples = BooleanField(name='sendOnlyClosedSamples')
    send_queue_interval = IntegerField(name='sendQueueInterval')
    tests = ListField(TextField(), name='tests')
    timeout_sec = IntegerField(name='timeoutSec')

    @property
    def directory(self):
        return 'externalSystem'


################################################################################


class FormLayout(DirectoryItem):
    byte_content = TextField(name='byteContent')
    content = TextField(name='content')
    layout_type = IntegerField(name='layoutType')

    @property
    def directory(self):
        return 'formLayout'


################################################################################


class PriceListInfo(Mapping):
    discount = FloatField(name='discount')
    hospital = RefField(name='hospital')
    id = IntegerField(name='id')
    pricelist = RefField(name='pricelist')
    start_date = DateTimeField(name='startDate')


class Hospital(DirectoryItem):
    account = TextField(name='account')
    accountant = TextField(name='accountant')
    agreement_nr = TextField(name='agreementNr')
    bank = TextField(name='bank')
    bik = TextField(name='bik')
    chief_doctor = TextField(name='chiefDoctor')
    corr_account = TextField(name='corrAccount')
    couriers = ListField(TextField(), name='couriers')
    cust_departments = ListField(RefField(), name='custDepartments')
    director = TextField(name='director')
    email = TextField(name='email')
    email_file_name_template = TextField(name='emailFileNameTemplate')
    email_file_type = IntegerField(name='emailFileType')
    email_need_response = BooleanField(name='emailNeedResponse')
    email_response = TextField(name='emailResponse')
    email_response_hard_copy = BooleanField(name='emailResponseHardCopy')
    email_response_request_count = IntegerField(name='emailResponseRequestCount')
    email_response_single_attachment = BooleanField(name='emailResponseSingleAttachment')
    email_skip_mail = BooleanField(name='emailSkipMail')
    email_storage_path = TextField(name='emailStoragePath')
    enable_result_storage = BooleanField(name='enableResultStorage')
    eng_accountant = TextField(name='engAccountant')
    eng_bank = TextField(name='engBank')
    eng_chief_doctor = TextField(name='engChiefDoctor')
    eng_director = TextField(name='engDirector')
    eng_fact_address = TextField(name='engFactAddress')
    eng_fullname = TextField(name='engFullname')
    eng_jur_address = TextField(name='engJurAddress')
    eng_name = TextField(name='engName')
    extra1 = TextField(name='extra1')
    extra2 = TextField(name='extra2')
    extra3 = TextField(name='extra3')
    extra4 = TextField(name='extra4')
    extra5 = TextField(name='extra5')
    fact_address = TextField(name='factAddress')
    fax = TextField(name='fax')
    fullname = TextField(name='fullname')
    id = IntegerField(name='id')
    inn = TextField(name='inn')
    jur_address = TextField(name='jurAddress')
    kpp = TextField(name='kpp')
    non_checked_services = ListField(TextField(), name='nonCheckedServices')
    number_format = TextField(name='numberFormat')
    object_factors = ListField(RefField(), name='objectFactors')
    okonh = TextField(name='okonh')
    okpo = TextField(name='okpo')
    pay_categories = ListField(TextField(), name='payCategories')
    phone = TextField(name='phone')
    pricelists = ListField(ObjectField(PriceListInfo), name='pricelists')
    print_form_graphics = ListField(TextField(), name='printFormGraphics')
    print_form_strings = ListField(TextField(), name='printFormStrings')
    print_forms = ListField(TextField(), name='printForms')
    skip_registration_check = BooleanField(name='skipRegistrationCheck')
    sync_user_directories = ListField(TextField(), name='syncUserDirectories')

    @property
    def directory(self):
        return 'hospital'


################################################################################


class HospitalFactor(Mapping):
    category = RefField(name='category')
    code = TextField(name='code')
    id = IntegerField(name='id')
    mnemonics = TextField(name='mnemonics')
    name = TextField(name='name')
    object_ids = ListField(RefField(), name='objectIds')
    removed = BooleanField(name='removed')
    system = BooleanField(name='system')


class HospitalCategory(DirectoryItem):
    default_category = BooleanField(name='defaultCategory')
    factors = ListField(ObjectField(HospitalFactor), name='factors')

    @property
    def directory(self):
        return 'hospitalCategory'


################################################################################


class Material(DirectoryItem):
    always_use_box_unit = BooleanField(name='alwaysUseBoxUnit')
    barcode = TextField(name='barcode')
    box_unit = RefField(name='boxUnit')
    catalog_nr = TextField(name='catalogNr')
    code_in1_c = TextField(name='codeIn1C')
    expiration_dates = ListField(TextField(), name='expirationDates')
    material_factors = ListField(TextField(), name='materialFactors')
    mol = TextField(name='mol')
    reserve = IntegerField(name='reserve')
    resource_type = IntegerField(name='resourceType')
    services = ListField(TextField(), name='services')
    tax = IntegerField(name='tax')
    tests = ListField(TextField(), name='tests')
    units_in_box = IntegerField(name='unitsInBox')

    @property
    def directory(self):
        return 'material'


################################################################################


class MaterialUnit(DirectoryItem):
    pass

    @property
    def directory(self):
        return 'materialUnit'


################################################################################


class MicroOrganism(DirectoryItem):
    pass

    @property
    def directory(self):
        return 'microOrganism'


################################################################################


class Outsourcer(DirectoryItem):
    departments = ListField(TextField(), name='departments')
    full_name = TextField(name='fullName')

    @property
    def directory(self):
        return 'outsourcer'


################################################################################


class PatientGroup(DirectoryItem):
    age_end = FloatField(name='ageEnd')
    age_start = FloatField(name='ageStart')
    age_unit = IntegerField(name='ageUnit')
    cycle_period = IntegerField(name='cyclePeriod')
    eng_name = TextField(name='engName')
    sex = IntegerField(name='sex')

    @property
    def directory(self):
        return 'patientGroup'


################################################################################


class PayCategoryValue(Mapping):
    discount = FloatField(name='discount')
    id = IntegerField(name='id')
    pay_category = RefField(name='payCategory')
    start_date = DateTimeField(name='startDate')


class PayCategory(DirectoryItem):
    category_type = IntegerField(name='categoryType')
    eng_name = TextField(name='engName')
    hospitals = ListField(RefField(), name='hospitals')
    non_checked_services = ListField(TextField(), name='nonCheckedServices')
    skip_registration_check = BooleanField(name='skipRegistrationCheck')
    values = ListField(ObjectField(PayCategoryValue), name='values')

    @property
    def directory(self):
        return 'payCategory'


################################################################################

class HospitalInfo(Mapping):
    discount = FloatField(name='discount')
    hospital = RefField(name='hospital')
    id = IntegerField(name='id')
    pricelist = RefField(name='pricelist')
    start_date = DateTimeField(name='startDate')


class PriceInfo(Mapping):
    duration = IntegerField(name='duration')
    id = IntegerField(name='id')
    price = FloatField(name='price')
    pricelist = RefField(name='pricelist')
    service = RefField(name='service')
    urgent_duration = IntegerField(name='urgentDuration')


class Pricelist(DirectoryItem):
    hospitals = ListField(ObjectField(HospitalInfo), name='hospitals')
    pay_categories = ListField(TextField(), name='payCategories')
    prices = ListField(ObjectField(PriceInfo), name='prices')
    urgent_factor = FloatField(name='urgentFactor')

    @property
    def directory(self):
        return 'pricelist'


################################################################################


class PricelistShort(DirectoryItem):
    hospitals = ListField(ObjectField(HospitalInfo), name='hospitals')
    pay_categories = ListField(TextField(), name='payCategories')
    urgent_factor = FloatField(name='urgentFactor')

    @property
    def directory(self):
        return 'pricelistShort'


################################################################################


class PrintFormHeader(DirectoryItem):
    default_header = BooleanField(name='defaultHeader')
    hospitals = ListField(RefField(), name='hospitals')
    template = TextField(name='template')

    @property
    def directory(self):
        return 'printFormHeader'


################################################################################


class FieldSort(Mapping):
    field_name = TextField(name='fieldName')
    id = IntegerField(name='id')
    order = BooleanField(name='order')
    rank = IntegerField(name='rank')


class DataSourceSort(Mapping):
    datasource_name = TextField(name='datasourceName')
    field_sorts = ListField(ObjectField(FieldSort), name='fieldSorts')
    id = IntegerField(name='id')


class PrintFormNew(DirectoryItem):
    abstract_print_form = BooleanField(name='abstractPrintForm')
    datasource_sorts = ListField(ObjectField(DataSourceSort), name='datasourceSorts')
    departments = ListField(TextField(), name='departments')
    full_inheritance = BooleanField(name='fullInheritance')
    hospitals = ListField(TextField(), name='hospitals')
    inherit_sortings = BooleanField(name='inheritSortings')
    object_type = IntegerField(name='objectType')
    param1 = TextField(name='param1')
    param2 = TextField(name='param2')
    param3 = TextField(name='param3')
    print_deleted = BooleanField(name='printDeleted')
    print_empty = BooleanField(name='printEmpty')
    reports = ListField(TextField(), name='reports')
    template = TextField(name='template')
    test_groups = ListField(TextField(), name='testGroups')

    @property
    def directory(self):
        return 'printFormNew'


################################################################################


class Profile(DirectoryItem):
    department = RefField(name='department')
    tests = ListField(RefField(), name='tests')

    @property
    def directory(self):
        return 'profile'


################################################################################


class QcAnalyte(DirectoryItem):
    cvg = FloatField(name='cvg')
    cvi = FloatField(name='cvi')
    max_b20 = FloatField(name='maxB20')
    max_cv20 = FloatField(name='maxCV20')

    @property
    def directory(self):
        return 'qcAnalyte'


################################################################################


class QcEvent(BaseDirectoryItem, RemovableMixIn, MnemonicsMixIn):
    pass

    @property
    def directory(self):
        return 'qcEvent'


################################################################################


class QcTestInfo(Mapping):
    cv = FloatField(name='cv')
    dx = FloatField(name='dx')
    id = IntegerField(name='id')
    max = FloatField(name='max')
    min = FloatField(name='min')
    s = FloatField(name='s')
    test_in_group = RefField(name='testInGroup')
    x = FloatField(name='x')


class QcLevelInfo(Mapping):
    control_nr = TextField(name='controlNr')
    id = IntegerField(name='id')
    name = TextField(name='name')
    rank = IntegerField(name='rank')
    removed = BooleanField(name='removed')
    tests = ListField(ObjectField(QcTestInfo), name='tests')


class QcMaterial(DirectoryItem):
    certified = BooleanField(name='certified')
    levels = ListField(ObjectField(QcLevelInfo), name='levels')
    material_tests = ListField(RefField(), name='materialTests')
    producer = RefField(name='producer')

    @property
    def directory(self):
        return 'qcMaterial'


################################################################################


class QcProducer(DirectoryItem):
    pass

    @property
    def directory(self):
        return 'qcProducer'


################################################################################


class QcTestRule(Mapping):
    across_levels = BooleanField(name='acrossLevels')
    id = IntegerField(name='id')
    rule_index = IntegerField(name='ruleIndex')


class QcTest(Mapping):
    apply_rules_for_setting = BooleanField(name='applyRulesForSetting')
    chart_cv = FloatField(name='chartCv')
    chart_mode = IntegerField(name='chartMode')
    diff_level1 = BooleanField(name='diffLevel1')
    diff_level2 = BooleanField(name='diffLevel2')
    diff_level3 = BooleanField(name='diffLevel3')
    diff_ost = BooleanField(name='diffOST')
    disable_setting = BooleanField(name='disableSetting')
    id = IntegerField(name='id')
    ignorable_normality = ListField(TextField(), name='ignorableNormality')
    ignorable_normality_int = IntegerField(name='ignorableNormalityInt')
    include_manual_results = BooleanField(name='includeManualResults')
    q_sum_s = BooleanField(name='qSumS')
    q_sum_s2 = BooleanField(name='qSumS2')
    removed = BooleanField(name='removed')
    restart_after_error = BooleanField(name='restartAfterError')
    rules = ListField(ObjectField(QcTestRule), name='rules')
    rules_after_warning = BooleanField(name='rulesAfterWarning')
    test = RefField(name='test')


class QcTestGroup(DirectoryItem):
    chart_cv = FloatField(name='chartCv')
    chart_mode = IntegerField(name='chartMode')
    department = RefField(name='department')
    equipment = RefField(name='equipment')
    tests = ListField(ObjectField(QcTest), name='tests')
    user_groups = ListField(RefField(), name='userGroups')

    @property
    def directory(self):
        return 'qcTestGroup'


################################################################################


class ReportGroup(Mapping):
    category_id = IntegerField(name='categoryId')
    group_by = IntegerField(name='groupBy')
    id = IntegerField(name='id')
    include_null = BooleanField(name='includeNull')
    items = ListField(IntegerField(), name='items')
    rank = IntegerField(name='rank')
    show_in_column = BooleanField(name='showInColumn')
    values = ListField(TextField(), name='values')


class Report(DirectoryItem):
    employees = ListField(RefField(), name='employees')
    groups = ListField(ObjectField(ReportGroup), name='groups')
    print_forms = ListField(TextField(), name='printForms')
    show_in_table = BooleanField(name='showInTable')
    source = IntegerField(name='source')
    use_delivery_date = BooleanField(name='useDeliveryDate')

    @property
    def directory(self):
        return 'report'



################################################################################


class TargetInfo(Mapping):
    id = IntegerField(name='id')
    rank = IntegerField(name='rank')
    target = RefField(name='target')


class RequestFormGroup(Mapping):
    button_down_color = IntegerField(name='buttonDownColor')
    button_up_color = IntegerField(name='buttonUpColor')
    id = IntegerField(name='id')
    name = TextField(name='name')
    rank = IntegerField(name='rank')
    targets = ListField(ObjectField(TargetInfo), name='targets')


class RequestForm(DirectoryItem):
    batch_mode = BooleanField(name='batchMode')
    button_caption = TextField(name='buttonCaption')
    button_height = IntegerField(name='buttonHeight')
    button_indent = IntegerField(name='buttonIndent')
    button_width = IntegerField(name='buttonWidth')
    can_select_targets = BooleanField(name='canSelectTargets')
    create_patient_and_card_if_not_found = BooleanField(name='createPatientAndCardIfNotFound')
    default_biomaterials = ListField(TextField(), name='defaultBiomaterials')
    default_targets = ListField(TextField(), name='defaultTargets')
    full_name_patient_search = BooleanField(name='fullNamePatientSearch')
    grid_columns = IntegerField(name='gridColumns')
    grid_rows = IntegerField(name='gridRows')
    groups = ListField(ObjectField(RequestFormGroup), name='groups')
    layout = RefField(name='layout')
    need_biomaterial = BooleanField(name='needBiomaterial')
    need_passport_data = BooleanField(name='needPassportData')
    print_batch_sample_barcodes = BooleanField(name='printBatchSampleBarcodes')
    print_batch_worklist_barcodes = BooleanField(name='printBatchWorklistBarcodes')
    priority_mode = IntegerField(name='priorityMode')
    request_nr_template = TextField(name='requestNrTemplate')
    save_hospital = BooleanField(name='saveHospital')
    show_batch_button = BooleanField(name='showBatchButton')
    show_copy_button = BooleanField(name='showCopyButton')
    show_estimated_time = BooleanField(name='showEstimatedTime')
    show_go_to_button = BooleanField(name='showGoToButton')
    show_new_button = BooleanField(name='showNewButton')
    show_print_barcode_button = BooleanField(name='showPrintBarcodeButton')
    show_priority = BooleanField(name='showPriority')
    show_reset_button = BooleanField(name='showResetButton')
    show_samples = BooleanField(name='showSamples')
    show_single_patient = BooleanField(name='showSinglePatient')
    show_single_patient_card = BooleanField(name='showSinglePatientCard')
    show_source = BooleanField(name='showSource')
    use_grouping = BooleanField(name='useGrouping')
    user_fields = ListField(RefField(), name='userFields')
    user_groups = ListField(RefField(), name='userGroups')

    @property
    def directory(self):
        return 'requestForm'


################################################################################


class ResultTestValue(Mapping):
    id = IntegerField(name='id')
    test = RefField(name='test')
    value = TextField(name='value')

class ResultCode(DirectoryItem):
    test_values = ListField(ObjectField(ResultTestValue), name='testValues')

    @property
    def directory(self):
        return 'resultCode'


################################################################################


class Element(Mapping):
    caption = TextField(name='caption')
    id = IntegerField(name='id')
    param1 = TextField(name='param1')
    param2 = TextField(name='param2')
    param3 = TextField(name='param3')
    rank = IntegerField(name='rank')
    required = BooleanField(name='required')
    show_if_absent = BooleanField(name='showIfAbsent')
    show_if_cancelled = BooleanField(name='showIfCancelled')
    test = RefField(name='test')


class Group(Mapping):
    band_name = TextField(name='bandName')
    code = TextField(name='code')
    elements = ListField(ObjectField(Element), name='elements')
    id = IntegerField(name='id')
    mnemonics = TextField(name='mnemonics')
    name = TextField(name='name')
    name_as_blank = BooleanField(name='nameAsBlank')
    name_as_target = BooleanField(name='nameAsTarget')
    param1 = TextField(name='param1')
    param2 = TextField(name='param2')
    param3 = TextField(name='param3')
    rank = IntegerField(name='rank')
    targets = ListField(RefField(), name='targets')


class SampleBlank(DirectoryItem):
    groups = ListField(ObjectField(Group), name='groups')
    print_form = RefField(name='printForm')
    targets = ListField(RefField(), name='targets')

    @property
    def directory(self):
        return 'sampleBlank'


################################################################################


class ScanFormElement(Mapping):
    allow_new = BooleanField(name='allowNew')
    allow_update = BooleanField(name='allowUpdate')
    code = TextField(name='code')
    element_type = IntegerField(name='elementType')
    field_index = IntegerField(name='fieldIndex')
    id = IntegerField(name='id')
    name = TextField(name='name')
    overwrite_patient_value = BooleanField(name='overwritePatientValue')
    use_code = BooleanField(name='useCode')
    user_field = RefField(name='userField')


class ScanFormInfo(Mapping):
    code = TextField(name='code')
    directory_groups = ListField(TextField(), name='directoryGroups')
    elements = ListField(ObjectField(ScanFormElement), name='elements')
    id = IntegerField(name='id')
    name = TextField(name='name')
    rank = IntegerField(name='rank')
    use_default_biomaterial_codes = BooleanField(name='useDefaultBiomaterialCodes')
    use_default_target_codes = BooleanField(name='useDefaultTargetCodes')


class ScanForm(BaseDirectoryItem, RemovableMixIn, MnemonicsMixIn):
    registration_form = RefField(name='registrationForm')
    scan_forms = ListField(ObjectField(ScanFormInfo), name='scanForms')

    @property
    def directory(self):
        return 'scanForm'


################################################################################


class Service(DirectoryItem):
    duration = IntegerField(name='duration')
    eng_name = TextField(name='engName')
    export_code = TextField(name='exportCode')
    resources = ListField(TextField(), name='resources')
    service_groups = ListField(TextField(), name='serviceGroups')
    targets = ListField(RefField(), name='targets')
    urgent_duration = IntegerField(name='urgentDuration')
    working_days = IntegerField(name='workingDays')

    @property
    def directory(self):
        return 'service'


################################################################################


class ServiceGroup(DirectoryItem):
    resources = ListField(RefField(), name='resources')
    services = ListField(RefField(), name='services')

    @property
    def directory(self):
        return 'serviceGroup'


################################################################################


class ServiceShort(DirectoryItem):
    duration = IntegerField(name='duration')
    eng_name = TextField(name='engName')
    export_code = TextField(name='exportCode')
    resources = ListField(RefField(), name='resources')
    service_groups = ListField(RefField(), name='serviceGroups')
    targets = ListField(RefField(), name='targets')
    urgent_duration = IntegerField(name='urgentDuration')
    working_days = IntegerField(name='workingDays')

    @property
    def directory(self):
        return 'serviceShort'


################################################################################


class Storage(Mapping):
    code = TextField(name='code')
    code_in1_c = TextField(name='codeIn1C')
    directory_groups = ListField(TextField(), name='directoryGroups')
    employees = ListField(TextField(), name='employees')
    id = IntegerField(name='id')
    main = BooleanField(name='main')
    mnemonics = TextField(name='mnemonics')
    name = TextField(name='name')
    removed = BooleanField(name='removed')

    @property
    def directory(self):
        return 'storage'


################################################################################


class Supplier(DirectoryItem):
    account = TextField(name='account')
    accountant = TextField(name='accountant')
    bank = TextField(name='bank')
    corr_account = TextField(name='corrAccount')
    director = TextField(name='director')
    email = TextField(name='email')
    fact_address = TextField(name='factAddress')
    fax = TextField(name='fax')
    fullname = TextField(name='fullname')
    inn = TextField(name='inn')
    jur_address = TextField(name='jurAddress')
    kpp = TextField(name='kpp')
    okonh = TextField(name='okonh')
    okpo = TextField(name='okpo')
    phone = TextField(name='phone')

    @property
    def directory(self):
        return 'supplier'

################################################################################


class Target(DirectoryItem):
    additional_tests = ListField(TextField(), name='additionalTests')
    biomaterials = ListField(RefField(), name='biomaterials')
    cancelled = BooleanField(name='cancelled')
    cito = BooleanField(name='cito')
    department = RefField(name='department')
    doctor_load = FloatField(name='doctorLoad')
    eng_name = TextField(name='engName')
    groups = ListField(TextField(), name='groups')
    lab_assist_load = FloatField(name='labAssistLoad')
    need_print = BooleanField(name='needPrint')
    observing_departments = ListField(RefField(), name='observingDepartments')
    regist_load = FloatField(name='registLoad')
    services = ListField(RefField(), name='services')
    target_type = IntegerField(name='targetType')
    tests = ListField(TextField(), name='tests')

    @property
    def directory(self):
        return 'target'


################################################################################


class TargetGroup(DirectoryItem):
    targets = ListField(RefField(), name='targets')

    @property
    def directory(self):
        return 'targetGroup'


################################################################################


class NumericRanges(Mapping):
    eng_name1 = TextField(name='engName1')
    eng_name2 = TextField(name='engName2')
    eng_name3 = TextField(name='engName3')
    eng_name4 = TextField(name='engName4')
    eng_name5 = TextField(name='engName5')
    eng_norm_name = TextField(name='engNormName')
    id = IntegerField(name='id')
    name1 = TextField(name='name1')
    name2 = TextField(name='name2')
    name3 = TextField(name='name3')
    name4 = TextField(name='name4')
    name5 = TextField(name='name5')
    norm_name = TextField(name='normName')
    patient_group = RefField(name='patientGroup')
    point2 = FloatField(name='point2')
    point3 = FloatField(name='point3')


class QcTestMapping(Mapping):
    code = TextField(name='code')
    equipment = RefField(name='equipment')
    id = IntegerField(name='id')
    qc_test_code = TextField(name='qcTestCode')
    test = RefField(name='test')


class Test(DirectoryItem):
    analyte = RefField(name='analyte')
    auto_approval = IntegerField(name='autoApproval')
    description = TextField(name='description')
    duration = IntegerField(name='duration')
    eng_name = TextField(name='engName')
    equipments = ListField(RefField(), name='equipments')
    exponential = BooleanField(name='exponential')
    format = TextField(name='format')
    hot_key = TextField(name='hotKey')
    need_print = BooleanField(name='needPrint')
    norms_text = TextField(name='normsText')
    numeric_ranges = ListField(ObjectField(NumericRanges), name='numericRanges')
    rank = IntegerField(name='rank')
    result_type = IntegerField(name='resultType')
    show_all_norms = IntegerField(name='showAllNorms')
    targets = ListField(RefField(), name='targets')
    test_mappings = ListField(ObjectField(QcTestMapping), name='testMappings')
    unit = RefField(name='unit')
    use_default_norm_comments = BooleanField(name='useDefaultNormComments')
    working_days = IntegerField(name='workingDays')

    @property
    def directory(self):
        return 'test'


################################################################################


class TestGroup(Mapping):
    id = IntegerField(name='id')
    rank = IntegerField(name='rank')
    show_if_absent = BooleanField(name='showIfAbsent')
    test = RefField(name='test')
    test_print_group = RefField(name='testPrintGroup')


class TestPrintGroup(DirectoryItem):
    band_name = TextField(name='bandName')
    eng_name = TextField(name='engName')
    param1 = TextField(name='param1')
    param2 = TextField(name='param2')
    param3 = TextField(name='param3')
    targets = ListField(TextField(), name='targets')
    test_groups = ListField(ObjectField(TestGroup), name='testGroups')

    @property
    def directory(self):
        return 'testPrintGroup'


################################################################################


class ResultTest(Mapping):
    apply_comment = BooleanField(name='applyComment')
    apply_if_approved = BooleanField(name='applyIfApproved')
    apply_if_done = BooleanField(name='applyIfDone')
    apply_if_exists = BooleanField(name='applyIfExists')
    apply_value = BooleanField(name='applyValue')
    auto_approval = IntegerField(name='autoApproval')
    comment = TextField(name='comment')
    create_new_work = BooleanField(name='createNewWork')
    id = IntegerField(name='id')
    test = RefField(name='test')
    test_rule = RefField(name='testRule')
    value = TextField(name='value')


class Value(Mapping):
    value = TextField(name='value')


class TestRule(DirectoryItem):
    approve_source = BooleanField(name='approveSource')
    normality = ListField(TextField(), name='normality')
    result_comment = TextField(name='resultComment')
    result_tests = ListField(ObjectField(ResultTest), name='resultTests')
    result_value = TextField(name='resultValue')
    source_test = RefField(name='sourceTest')
    values = ListField(ObjectField(Value), name='values')

    @property
    def directory(self):
        return 'testRule'


################################################################################


class Column(Mapping):
    auto_size = BooleanField(name='autoSize')
    auto_sort = BooleanField(name='autoSort')
    caption = TextField(name='caption')
    field_type = IntegerField(name='fieldType')
    fixed = BooleanField(name='fixed')
    fixed_width = BooleanField(name='fixedWidth')
    format = TextField(name='format')
    id = IntegerField(name='id')
    layout = RefField(name='layout')
    rank = IntegerField(name='rank')
    toggle_sort = BooleanField(name='toggleSort')
    width = IntegerField(name='width')


class TreeViewLayout(Mapping):
    columns = ListField(ObjectField(Column), name='columns')
    directory_groups = ListField(TextField(), name='directoryGroups')
    id = IntegerField(name='id')
    tree_type = IntegerField(name='treeType')

    @property
    def directory(self):
        return 'treeViewLayout'


################################################################################


class Unit(DirectoryItem):
    eng_name = TextField(name='engName')

    @property
    def directory(self):
        return 'unit'


################################################################################


class UserDirectoryValue(Mapping):
    code = TextField(name='code')
    export_code = TextField(name='exportCode')
    extra1 = TextField(name='extra1')
    extra2 = TextField(name='extra2')
    id = IntegerField(name='id')
    mnemonics = TextField(name='mnemonics')
    name = TextField(name='name')
    removed = BooleanField(name='removed')
    user_directory = RefField(name='userDirectory')


class UserDirectory(DirectoryItem):
    category = TextField(name='category')
    description = TextField(name='description')
    extra1_name = TextField(name='extra1Name')
    extra2_name = TextField(name='extra2Name')
    user_groups = ListField(RefField(), name='userGroups')
    values = ListField(ObjectField(UserDirectoryValue), name='values')

    @property
    def directory(self):
        return 'userDirectory'


################################################################################


class UserField(DirectoryItem):
    allow_batch_edit = BooleanField(name='allowBatchEdit')
    collection = BooleanField(name='collection')
    field_type = IntegerField(name='fieldType')
    load_in_request_forms = ListField(RefField(), name='loadInRequestForms')
    load_in_request_journal = BooleanField(name='loadInRequestJournal')
    load_in_samples = ListField(TextField(), name='loadInSamples')
    load_in_work_journals = ListField(TextField(), name='loadInWorkJournals')
    object_type = IntegerField(name='objectType')
    reference = BooleanField(name='reference')
    simple = BooleanField(name='simple')
    user_directory = RefField(name='userDirectory')

    @property
    def directory(self):
        return 'userField'


################################################################################


class UserGroup(Mapping):
    directory_groups = ListField(TextField(), name='directoryGroups')
    employees = ListField(RefField(), name='employees')
    id = IntegerField(name='id')
    name = TextField(name='name')
    rights = ListField(RefField(), name='rights')

    @property
    def directory(self):
        return 'userGroup'


################################################################################


class UserRule(DirectoryItem):
    action_text = TextField(name='actionText')
    description = TextField(name='description')
    formula_text = TextField(name='formulaText')

    @property
    def directory(self):
        return 'userRule'


################################################################################


class Position(Mapping):
    all_tests = BooleanField(name='allTests')
    control_lot_nr = TextField(name='controlLotNr')
    id = IntegerField(name='id')
    reserved = BooleanField(name='reserved')
    tests = ListField(RefField(), name='tests')
    x = IntegerField(name='x')
    y = IntegerField(name='y')


class Rack(Mapping):
    calc_result1_caption = TextField(name='calcResult1Caption')
    calc_result2_caption = TextField(name='calcResult2Caption')
    cell_format = TextField(name='cellFormat')
    code = TextField(name='code')
    comment1_caption = TextField(name='comment1Caption')
    comment2_caption = TextField(name='comment2Caption')
    consecutive_numbering = BooleanField(name='consecutiveNumbering')
    debug = BooleanField(name='debug')
    equipment_code = TextField(name='equipmentCode')
    expire_date = DateTimeField(name='expireDate')
    fill_mode = IntegerField(name='fillMode')
    finalization_code = TextField(name='finalizationCode')
    finalization_code_bytes = TextField(name='finalizationCodeBytes')
    full_racks = BooleanField(name='fullRacks')
    global_code = TextField(name='globalCode')
    global_code_bytes = TextField(name='globalCodeBytes')
    height = IntegerField(name='height')
    id = IntegerField(name='id')
    initialization_code = TextField(name='initializationCode')
    initialization_code_bytes = TextField(name='initializationCodeBytes')
    interpretation_type = IntegerField(name='interpretationType')
    main = BooleanField(name='main')
    method_name = TextField(name='methodName')
    operator_mode = IntegerField(name='operatorMode')
    parameter_values = ListField(TextField(), name='parameterValues')
    pcr_controls = ListField(TextField(), name='pcrControls')
    plate_values = ListField(TextField(), name='plateValues')
    positions = ListField(ObjectField(Position), name='positions')
    print_forms = ListField(RefField(), name='printForms')
    reading_properties = TextField(name='readingProperties')
    removed = BooleanField(name='removed')
    sample_code = TextField(name='sampleCode')
    sample_code_bytes = TextField(name='sampleCodeBytes')
    sample_height = IntegerField(name='sampleHeight')
    sample_values = ListField(TextField(), name='sampleValues')
    sample_width = IntegerField(name='sampleWidth')
    total_count = IntegerField(name='totalCount')
    width = IntegerField(name='width')
    x_numbering_type = IntegerField(name='xNumberingType')
    y_numbering_type = IntegerField(name='yNumberingType')


class WorklistTestInfo(Mapping):
    id = IntegerField(name='id')
    rank = IntegerField(name='rank')
    test = RefField(name='test')


class WorklistDef(DirectoryItem):
    all_batch_worklists = BooleanField(name='allBatchWorklists')
    all_user_groups = BooleanField(name='allUserGroups')
    allow_change_tests = BooleanField(name='allowChangeTests')
    allow_drop = BooleanField(name='allowDrop')
    approve_all_tests = BooleanField(name='approveAllTests')
    approve_all_values = BooleanField(name='approveAllValues')
    auto_code = BooleanField(name='autoCode')
    auto_code_format = TextField(name='autoCodeFormat')
    auto_print_sample_barcode_on_add = BooleanField(name='autoPrintSampleBarcodeOnAdd')
    batch_worklists = ListField(TextField(), name='batchWorklists')
    biomaterials = ListField(TextField(), name='biomaterials')
    check_user_on_registration = BooleanField(name='checkUserOnRegistration')
    default_department_nr_exist = IntegerField(name='defaultDepartmentNrExist')
    department = RefField(name='department')
    divider_position = IntegerField(name='dividerPosition')
    full_racks_on_registration = BooleanField(name='fullRacksOnRegistration')
    patients_count = IntegerField(name='patientsCount')
    pcr_mode = BooleanField(name='pcrMode')
    pcr_print_forms = ListField(RefField(), name='pcrPrintForms')
    print_forms = ListField(RefField(), name='printForms')
    rack_print_caption = TextField(name='rackPrintCaption')
    rack_print_hint = TextField(name='rackPrintHint')
    racks = ListField(ObjectField(Rack), name='racks')
    reading_properties = TextField(name='readingProperties')
    results_print_caption = TextField(name='resultsPrintCaption')
    results_print_hint = TextField(name='resultsPrintHint')
    search_by_code = BooleanField(name='searchByCode')
    send_to_equipment = BooleanField(name='sendToEquipment')
    show_pcr_nr = BooleanField(name='showPcrNr')
    show_pcr_test_info = BooleanField(name='showPcrTestInfo')
    skip_show_in_process_view = BooleanField(name='skipShowInProcessView')
    tests = ListField(ObjectField(WorklistTestInfo), name='tests')
    tests_count = IntegerField(name='testsCount')
    use_on_registration = BooleanField(name='useOnRegistration')
    user_fields = ListField(TextField(), name='userFields')
    user_groups = ListField(TextField(), name='userGroups')

    @property
    def directory(self):
        return 'worklistDef'


################################################################################


class WorkListDefInfo(Mapping):
    id = IntegerField(name='id')
    rank = IntegerField(name='rank')
    worklist = RefField(name='worklist')


class WorklistDefGroup(DirectoryItem):
    rank = IntegerField(name='rank')
    worklist_defs = ListField(ObjectField(WorkListDefInfo), name='worklistDefs')

    @property
    def directory(self):
        return 'worklistDefGroup'


################################################################################
