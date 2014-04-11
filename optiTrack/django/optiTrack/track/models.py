# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Tbldept(models.Model):
    deptid = models.AutoField(primary_key=True, db_column='DeptID') # Field name made lowercase.
    deptcode = models.CharField(max_length=50L, db_column='DeptCode', blank=True) # Field name made lowercase.
    deptnum = models.CharField(max_length=50L, db_column='DeptNum', blank=True) # Field name made lowercase.
    deptdescription = models.CharField(max_length=50L, db_column='DeptDescription', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'tbldept'

    def __unicode__(self):
        return self.deptcode

class Tblemployee(models.Model):
    employeeid = models.AutoField(primary_key=True, db_column='EmployeeID') # Field name made lowercase.
    lastname = models.CharField(max_length=50L, db_column='LastName', blank=True) # Field name made lowercase.
    firstname = models.CharField(max_length=50L, db_column='FirstName', blank=True) # Field name made lowercase.
    department = models.CharField(max_length=50L, db_column='Department', blank=True) # Field name made lowercase.
    notactive = models.TextField(db_column='NotActive', blank=True) # Field name made lowercase. This field type is a guess.
    class Meta:
        db_table = 'tblemployee'

    def __unicode__(self):
        return self.firstname + ' ' + self.lastname

class Tblholidays(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID') # Field name made lowercase.
    holidaydate = models.DateTimeField(null=True, db_column='HolidayDate', blank=True) # Field name made lowercase.
    holidaydescription = models.CharField(max_length=255L, db_column='HolidayDescription', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'tblholidays'

    def __unicode__(self):
        return self.holidaydate

class Tbljobinfo(models.Model):
    jobid = models.AutoField(primary_key=True, db_column='JobID') # Field name made lowercase.
    customer = models.CharField(max_length=50L, db_column='Customer', blank=True) # Field name made lowercase.
    project = models.CharField(max_length=50L, db_column='Project', blank=True) # Field name made lowercase.
    elementname = models.CharField(max_length=50L, db_column='ElementName', blank=True) # Field name made lowercase.
    partdrawingnumber = models.CharField(max_length=50L, db_column='PartDrawingNumber', blank=True) # Field name made lowercase.
    partdrawingrev = models.CharField(max_length=50L, db_column='PartDrawingRev', blank=True) # Field name made lowercase.
    partdrawingrevdate = models.DateTimeField(null=True, db_column='PartDrawingRevDate', blank=True) # Field name made lowercase.
    jobcomplete = models.TextField(db_column='JobComplete', blank=True) # Field name made lowercase. This field type is a guess.
    jobselect = models.TextField(db_column='JobSelect', blank=True) # Field name made lowercase. This field type is a guess.
    employeeid = models.IntegerField(null=True, db_column='EmployeeID', blank=True) # Field name made lowercase.
    travelerrev = models.CharField(max_length=255L, db_column='TravelerRev', blank=True) # Field name made lowercase.
    travelerrevdate = models.DateTimeField(null=True, db_column='TravelerRevDate', blank=True) # Field name made lowercase.
    sbsqntworkcycdays = models.IntegerField(null=True, db_column='SbsqntWorkCycDays', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'tbljobinfo'

    def __unicode__(self):
        return self.jobid

class Tblpartsn(models.Model):
    partid = models.AutoField(primary_key=True, db_column='PartID') # Field name made lowercase.
    jobid = models.IntegerField(null=True, db_column='JobID', blank=True) # Field name made lowercase.
    soid = models.IntegerField(null=True, db_column='SOID', blank=True) # Field name made lowercase.
    partsn = models.CharField(max_length=50L, db_column='PartSN', blank=True) # Field name made lowercase.
    surfdescription = models.CharField(max_length=50L, db_column='SurfDescription', blank=True) # Field name made lowercase.
    custreqdate = models.DateTimeField(null=True, db_column='CustReqDate', blank=True) # Field name made lowercase.
    adjsbsqntworkdays = models.IntegerField(null=True, db_column='AdjsbsqntWorkDays', blank=True) # Field name made lowercase.
    prodordnum = models.IntegerField(null=True, db_column='ProdOrdNum', blank=True) # Field name made lowercase.
    partreleasedate = models.DateTimeField(null=True, db_column='PartReleaseDate', blank=True) # Field name made lowercase.
    partdatedone = models.DateTimeField(null=True, db_column='PartDateDone', blank=True) # Field name made lowercase.
    partpoclosed = models.TextField(db_column='PartPOClosed', blank=True) # Field name made lowercase. This field type is a guess.
    class Meta:
        db_table = 'tblpartsn'

    def __unicode__(self):
        return self.partid

class Tblprocessstatus(models.Model):
    processstatusid = models.AutoField(primary_key=True, db_column='ProcessStatusID') # Field name made lowercase.
    pstatusdesc = models.CharField(max_length=50L, db_column='PStatusDesc', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'tblprocessstatus'

    def __unicode__(self):
        return self.pstatusdesc

class Tblresources(models.Model):
    resid = models.AutoField(primary_key=True, db_column='ResID') # Field name made lowercase.
    resname = models.CharField(max_length=255L, db_column='ResName', blank=True) # Field name made lowercase.
    ressetup = models.CharField(max_length=255L, db_column='ResSetup', blank=True) # Field name made lowercase.
    resmemo = models.TextField(db_column='ResMemo', blank=True) # Field name made lowercase.
    deptid = models.IntegerField(null=True, db_column='DeptID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'tblresources'

    def __unicode__(self):
        return self.resname

class Tblsalesorder(models.Model):
    soid = models.IntegerField(null=True, db_column='SOID', blank=True) # Field name made lowercase.
    customer_po = models.CharField(max_length=255L, db_column='Customer_PO', blank=True) # Field name made lowercase.
    order_no = models.CharField(max_length=255L, db_column='Order_No', blank=True) # Field name made lowercase.
    pos = models.IntegerField(null=True, db_column='Pos', blank=True) # Field name made lowercase.
    item_code = models.CharField(max_length=255L, db_column='Item_Code', blank=True) # Field name made lowercase.
    item_description = models.CharField(max_length=255L, db_column='Item_Description', blank=True) # Field name made lowercase.
    pldlvry = models.DateTimeField(null=True, db_column='PLDlvry', blank=True) # Field name made lowercase.
    curr_req_dt = models.DateTimeField(null=True, db_column='Curr_Req_DT', blank=True) # Field name made lowercase.
    orig_prom_dt = models.DateTimeField(null=True, db_column='Orig_Prom_DT', blank=True) # Field name made lowercase.
    order_date = models.DateTimeField(null=True, db_column='Order_Date', blank=True) # Field name made lowercase.
    datagenerated = models.DateTimeField(null=True, db_column='DataGenerated', blank=True) # Field name made lowercase.
    soclosed = models.TextField(db_column='SOClosed', blank=True) # Field name made lowercase. This field type is a guess.
    class Meta:
        db_table = 'tblsalesorder'

    def __unicode__(self):
        return self.order_no

class Tblschedule(models.Model):
    skedid = models.IntegerField(null=True, db_column='SkedID', blank=True) # Field name made lowercase.
    partid = models.IntegerField(null=True, db_column='PartID', blank=True) # Field name made lowercase.
    workid = models.IntegerField(null=True, db_column='WorkID', blank=True) # Field name made lowercase.
    duedate = models.DateTimeField(null=True, db_column='DueDate', blank=True) # Field name made lowercase.
    cmpadjdays = models.IntegerField(null=True, db_column='CmpAdjDays', blank=True) # Field name made lowercase.
    plnduedate = models.DateTimeField(null=True, db_column='PlnDueDate', blank=True) # Field name made lowercase.
    plnadjdays = models.IntegerField(null=True, db_column='PlnAdjDays', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'tblschedule'

    def __unicode__(self):
        return self.skedid

class Tblstatus(models.Model):
    statid = models.IntegerField(null=True, db_column='StatID', blank=True) # Field name made lowercase.
    partid = models.ForeignKey(Tblpartsn, null=True, db_column='PartID', blank=True) # Field name made lowercase.
    workid = models.ForeignKey('Tblworkins', null=True, db_column='WorkID', blank=True) # Field name made lowercase.
    opstart = models.DateTimeField(null=True, db_column='OpStart', blank=True) # Field name made lowercase.
    opstop = models.DateTimeField(null=True, db_column='OpStop', blank=True) # Field name made lowercase.
    processstatusid = models.ForeignKey(Tblprocessstatus, null=True, db_column='ProcessStatusID', blank=True) # Field name made lowercase.
    itrmap = models.CharField(max_length=50L, db_column='ItrMap', blank=True) # Field name made lowercase.
    surferror = models.FloatField(null=True, db_column='SurfError', blank=True) # Field name made lowercase.
    comment = models.CharField(max_length=75L, db_column='Comment', blank=True) # Field name made lowercase.
    current = models.TextField(db_column='Current', blank=True) # Field name made lowercase. This field type is a guess.
    class Meta:
        db_table = 'tblstatus'

    def __unicode__(self):
        return self.statid

class Tblwiresdetail(models.Model):
    wiresdetailid = models.AutoField(primary_key=True, db_column='WIResDetailID') # Field name made lowercase.
    workid = models.ForeignKey('Tblworkins', null=True, db_column='WorkID', blank=True) # Field name made lowercase.
    resid = models.ForeignKey(Tblresources, null=True, db_column='ResID', blank=True) # Field name made lowercase.
    reshoursneeded = models.FloatField(null=True, db_column='ResHoursNeeded', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'tblwiresdetail'

    def __unicode__(self):
        return self.wiresdetailid

class Tblwiskilldetail(models.Model):
    wiskilldetailid = models.AutoField(primary_key=True, db_column='WISkillDetailID') # Field name made lowercase.
    skilldetailid = models.IntegerField(null=True, db_column='SkillDetailID', blank=True) # Field name made lowercase.
    workid = models.ForeignKey('Tblworkins', null=True, db_column='WorkId', blank=True) # Field name made lowercase.
    skillhrsneeded = models.FloatField(null=True, db_column='SkillHrsNeeded', blank=True) # Field name made lowercase.
    skilllevel = models.CharField(max_length=50L, db_column='SkillLevel', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'tblwiskilldetail'

    def __unicode__(self):
        return self.wiskilldetailid

class Tblworkins(models.Model):
    workid = models.AutoField(primary_key=True, db_column='WorkID') # Field name made lowercase.
    jobid = models.ForeignKey(Tbljobinfo, null=True, db_column='JobID', blank=True) # Field name made lowercase.
    deptid = models.ForeignKey(Tbldept, null=True, db_column='DeptID', blank=True) # Field name made lowercase.
    opnum = models.CharField(max_length=50L, db_column='OpNum', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=50L, db_column='Description', blank=True) # Field name made lowercase.
    cycledays = models.IntegerField(null=True, db_column='CycleDays', blank=True) # Field name made lowercase.
    wirevision = models.CharField(max_length=50L, db_column='WIRevision', blank=True) # Field name made lowercase.
    kbid = models.IntegerField(null=True, db_column='KBID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'tblworkins'

    def __unicode__(self):
        return self.workid
