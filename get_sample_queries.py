def get_sample_queries():
    """Get sample SQL queries for training"""
    return [
        """
        -- truncate table coupa_contracts
delete from coupa_contracts where [Contract Header] IN ('Contract Party','Contract Party Contact')
        """,
        """
        -- enriched payment terms from elevate for contracts that have blank  (exclude BAA and NDA's and Care AT Home)
select distinct c.[Contract #], [Contract Name],e.[Payment Terms] as Enriched_Payment_Terms,Starts,Expires,s.[Supplier #] ,s.Name,s.Status as COUPA_Status from coupa_contracts c left join COUPA_Suppliers s on c.[Supplier Number]=s.[Supplier #] left join [dbo].[Enrichment of Payment term_Phase 2&3_20240606_v2] e on c.[Contract #]=e.[Contract #] where c.[Payment Terms]='' and c.[Contract #] like 'OL%' and isnull(e.[Payment Terms],'')=''
        """,
        """
        -- total 3542 OL only ,
select * from [Enrichment of Payment term_Phase 2&3_20240606_v2] where [Payment Terms]=''
        """,
        """
        -- 5446
select [Contract #],[Payment Terms] from coupa_contracts c where [Payment Terms]='' and [Contract #] like 'OL%'
        """,
        """
        -- 3542 total number of contracts missing payment terms ~800 elevate enriching 288 Manisha to try reloading , these have terms in enriched file 1428 contracts in elevate file did not have payment terms 1026 we need to track (these could be parent that have amendments so we did not update them or they have terms that do not exist in coupa)
select * from coupa_contracts where
        """,
        """
        select [Contract #],[Payment Terms] from coupa_contracts c where exists (Select 'x' from [Enrichment of Payment term_Phase 2&3_20240606_v2] e where c.[Contract #]=e.[Contract #] and e.[Payment Terms]<>'') and c.[Payment Terms]='' and [Contract #] like 'OL%'
        """,
        """
        -- 288
select distinct [Contract #],[Payment Terms] from coupa_contracts where [Contract Type Name] like 'BAA%' and [Contract #] like 'OL%' and [Payment Terms]<>''
        """,
        """
        -- 63 new suppliers list that Wendy sent (find contracts if any in the enriched list and COUPA, supplier status in coupa) get 10 contracts per contract type for Bill
select distinct [Contract #] from coupa_contracts where [Contract #] like 'OL%' and [Contract Type Name]  in ('Lease/Rental Agreement','MSA - Master Services Agreement','Site License' ,'SWLA - Software License Agreement','VOF - Vendor Order Form','Purchase Agreement','BAA - Business Associate Agreement' ,'MPRODS - Master Products/Services Agreement','LOA - Letter of Agreement','Service Agreement','SOW - Statement of Work')
        """,
        """
        WITH TOPTEN AS ( SELECT [Contract #],[Contract Type Name],[Contract Name],[Supplier Name], ROW_NUMBER() over ( PARTITION BY [Contract Type Name] order by [Contract #],[Contract Type Name] ) AS RowNo FROM coupa_contracts where [Contract #] like 'OL%' and [Contract Type Name]  in ('Lease/Rental Agreement','MSA - Master Services Agreement','Site License' ,'SWLA - Software License Agreement','VOF - Vendor Order Form','Purchase Agreement','BAA - Business Associate Agreement' ,'MPRODS - Master Products/Services Agreement','LOA - Letter of Agreement','Service Agreement','SOW - Statement of Work')
        """,
        """
        ) SELECT * FROM TOPTEN WHERE RowNo <= 10
        """,
        """
        select * from OneLink_Master_New where [Contract #]='OL_DOC591'
        """,
        """
        -- count of contracts with blank supplier ID
select distinct  [Contract Type Name],[Contract #],[Contract Name],[Supplier Number],description, Starts,Expires from OneLink_Master_New where [Contract Type Name] in ('BAA - Business Associate Agreement','NDA - Mutual Non-Disclosure Agreement','LOA - Letter of Agreement') and [Supplier Number]=''
        """,
        """
        -- contracts that is not in coupa
select distinct [Contract Type Name],[Contract #],[Contract Name],[Supplier Number],description, Starts,Expires from OneLink_Master_New o where [Contract Type Name] in ('BAA - Business Associate Agreement','NDA - Mutual Non-Disclosure Agreement','LOA - Letter of Agreement') and not exists (Select 'x' from coupa_contracts c where o.[Contract #]=c.[Contract #]) and len([Supplier Number])>2
        """,
        """
        -- contracts that can be loaded into COUPA
select * from (select distinct [Contract #],[Contract Type Name],[Supplier Number],description, Starts,Expires from OneLink_Master_New o where [Contract Type Name] in ('BAA - Business Associate Agreement') and not exists (Select 'x' from coupa_contracts c where o.[Contract #]=c.[Contract #]) and len([Supplier Number])>2) a where exists (Select 'X' from COUPA_Suppliers s where a.[Supplier Number]=s.[Supplier #])
        """,
        """
        select * from (select distinct [Contract #],[Contract Type Name],[Supplier Number],description, Starts,Expires from OneLink_Master_New o where [Contract Type Name] in ('NDA - Mutual Non-Disclosure Agreement') and not exists (Select 'x' from coupa_contracts c where o.[Contract #]=c.[Contract #]) and len([Supplier Number])>2) a where exists (Select 'X' from COUPA_Suppliers s where a.[Supplier Number]=s.[Supplier #])
        """,
        """
        select * from (select distinct [Contract #],[Contract Type Name],[Supplier Number],description, Starts,Expires from OneLink_Master_New o where [Contract Type Name] in ('LOA - Letter of Agreement') and not exists (Select 'x' from coupa_contracts c where o.[Contract #]=c.[Contract #]) and len([Supplier Number])>2) a where exists (Select 'X' from COUPA_Suppliers s where a.[Supplier Number]=s.[Supplier #])
        """,
        """
        -- count of contracts with blank supplier ID (NDA that is not in COUPA)
select distinct  [Contract Type Name],[Contract #],[Contract Name],[Supplier Number],description, Starts,Expires from OneLink_Master_New o where [Contract Type Name]='NDA - Mutual Non-Disclosure Agreement' and [Supplier Number]='' and not exists (Select 'X' from coupa_contracts c where o.[Contract #]=c.[Contract #])
        """,
        """
        -- create supplier missing file for BAA (for ones with supplier number)
select distinct [Contract #],[Contract Name],[Supplier Number],s.Name,o.NAME1 from [dbo].[BAA_MigrationPending] b left join COUPA_Suppliers s on ltrim(rtrim(b.[Supplier Number]))=ltrim(rtrim(s.[Supplier #])) left join OL_Supplier_Master o on ltrim(rtrim(b.[Supplier Number]))=ltrim(rtrim(o.VENDOR_ID)) where [Supplier Name]=''
        """,
        """
        select [Contract #],[Contract Name],s.[Supplier #],b.[Supplier Name],s.Name,o.NAME1 from [dbo].[BAA_MigrationPending] b left join COUPA_Suppliers s on ltrim(rtrim(b.[Supplier Name]))=ltrim(rtrim(s.Name)) left join OL_Supplier_Master o on ltrim(rtrim(b.[Supplier Name]))=ltrim(rtrim(o.NAME1)) where [Supplier Name]<>''
        """,
        """
        -- seeing some double spaces
update [dbo].[BAA_MigrationPending] set [Supplier Name]=replace([Supplier Name],'.','') where [Supplier Name]<>''
        """,
        """
        update [dbo].[BAA_MigrationPending] set [Supplier Name]=replace([Supplier Name],'  ',' ') where [Supplier Name]<>''
        """,
        """
        select distinct c.[Contract Type Name],b.[Contract #],b.[Supplier Number],c.Expires,b.[Supplier Name],s.Name as COUPA_Name,s.Status, o.NAME1 as OL_Name from [dbo].[BAA_MigrationPending] b left join COUPA_Suppliers s on ltrim(rtrim(b.[Supplier Name]))=ltrim(rtrim(s.Name)) left join OL_Supplier_Master o on ltrim(rtrim(b.[Supplier Name]))=ltrim(rtrim(o.NAME1)) left join OneLink_Master_New c on b.[Contract #]=c.[Contract #] where isnull(b.[Supplier Name],'')<>''
        """,
        """
        select * from coupa_suppliers where name like '%autonomy%'
        """,
        """
        select * from OL_Supplier_Master where NAME1 like '%abbott%'
        """,
        """
        select * from coupa_contracts where [Contract Type Name] ='BAA - Business Associate Agreement' and [Contract #] like 'OL%'
        """,
        """
        -- CONTRACTS NOT IN COUPA POPULATED
truncate table Contracts_NotInCOUPA
        """,
        """
        insert into  Contracts_NotInCOUPA select distinct [Contract Type Name],[Contract #],[Supplier Number],Expires,'','','','','','','','','' from [dbo].[OneLink_Contract_Union_Full] o where not exists (Select 'x' from coupa_contracts c where c.[Contract #]=o.[Contract #]) and [Contract Type Name] in ('MSA - Master Services Agreement','5/11/2018','SWLA - Software License Agreement','EQUIPMA - Equipment Maintenanc' ,'TECH - Technology Evaluation Agreement','VOF - Vendor Order Form','SEA - Single Entity Agreement','BAA - Business Associate Agreement' ,'NDA - Mutual Non-Disclosure Agreement','','MPRODS - Master Products/Services Agreement','LOA - Letter of Agreement','Services Agreement' ,'ConSignA - Consignment Agreement','SOW - Statement of Work')
        """,
        """
        -- (1277 rows affected)
insert into  Contracts_NotInCOUPA select distinct o.[Contract Type Name],o.[Contract #],o.[Supplier Number],o.Expires,'','','','','','','','','' from [dbo].[OneLink_Contract_Union_Full] o left join  coupa_contracts c on c.[Contract #]=replace(replace(o.[Contract #],'OL_HIC','CAH_'),'OL','CAH') where o.[Contract Type Name] in ('NSA - National Supplier Agreement','PPA - Participant Plan Agreement') and c.[Contract #] is null
        """,
        """
        -- 32 rows
select distinct [Contract Type Name] from Contracts_NotInCOUPA
        """,
        """
        select distinct [Contract #], [Contract Type Name] from coupa_contracts where [Contract #] like '%13097%'
        """,
        """
        -- and [Contract Type Name] ='BAA - Business Associate Agreement' 1999
update Contracts_NotInCOUPA set Enirched_Supplier_Name=b.[Supplier Name] from Contracts_NotInCOUPA c inner join [dbo].[BAA_MigrationPending] b on ltrim(rtrim(c.[Contract #]))=ltrim(rtrim(b.[Contract #]))
        """,
        """
        -- (764 rows affected)
update Contracts_NotInCOUPA set Enirched_Supplier_Number=b.[Supplier Number] from Contracts_NotInCOUPA c inner join [dbo].[BAA_MigrationPending] b on ltrim(rtrim(c.[Contract #]))=ltrim(rtrim(b.[Contract #]))
        """,
        """
        -- (764 rows affected)
update Contracts_NotInCOUPA set [Enirched_Supplier_Number]=e.[Supplier Number] from Contracts_NotInCOUPA c inner join [dbo].[Contracts Not In COUPA 07222024 Elevate Update] e on ltrim(rtrim(c.[Contract #]))=ltrim(rtrim(e.[Contract #])) where isnull(c.[Enirched_Supplier_Number],'')='' or c.[Enirched_Supplier_Number]='NULL'
        """,
        """
        -- (320 rows affected)
update Contracts_NotInCOUPA set [Enirched_Supplier_Name]=e.[COUPA_Supplier_Name] from Contracts_NotInCOUPA c inner join [dbo].[Contracts Not In COUPA 07222024 Elevate Update] e on ltrim(rtrim(c.[Contract #]))=ltrim(rtrim(e.[Contract #])) where isnull(c.[Enirched_Supplier_Name],'')='' or c.[Enirched_Supplier_Name]='NULL'
        """,
        """
        -- (320 rows affected)
update Contracts_NotInCOUPA set final_supplier_number=ltrim(rtrim(case when isnull([Supplier Number],'')='' then Enirched_Supplier_Number else [Supplier Number] end))
        """,
        """
        -- (1309 rows affected)
update Contracts_NotInCOUPA set final_supplier_name=ltrim(rtrim([Enirched_Supplier_Name]))
        """,
        """
        -- (1309 rows affected)
update Contracts_NotInCOUPA set replacement_supplier_number=r.[Replacement ID] from Contracts_NotInCOUPA c inner join ReplacementVendors20240408 r on c.final_supplier_number=r.Vendor_Id
        """,
        """
        -- (6 rows affected)
update Contracts_NotInCOUPA set final_supplier_number_new=ltrim(rtrim(case when isnull(replacement_supplier_number,'')='' then final_supplier_number else replacement_supplier_number end))
        """,
        """
        -- (1309 rows affected)
update Contracts_NotInCOUPA set coupa_supplier_name=null
        """,
        """
        update Contracts_NotInCOUPA set coupa_supplier_name=s.Name, COUPA_Supplier_Status=s.Status from Contracts_NotInCOUPA c inner join COUPA_Suppliers s on ltrim(rtrim(c.final_supplier_number_new))=ltrim(rtrim(s.[Supplier #])) where s.[Supplier #]<>''
        """,
        """
        -- (141 rows affected)
select distinct coupa_supplier_name,COUPA_Supplier_Status from Contracts_NotInCOUPA order by 1,2
        """,
        """
        update Contracts_NotInCOUPA set coupa_supplier_name=s.Name from Contracts_NotInCOUPA c inner join COUPA_Suppliers s on ltrim(rtrim(c.final_supplier_name))=ltrim(rtrim(s.Name)) where isnull(coupa_supplier_name,'')=''
        """,
        """
        -- (32 rows affected) update coupa status
update Contracts_NotInCOUPA set coupa_supplier_status=s.Status from Contracts_NotInCOUPA c inner join COUPA_Suppliers s on ltrim(rtrim(c.coupa_supplier_name))=ltrim(rtrim(s.name)) where isnull(COUPA_Supplier_Status,'')=''
        """,
        """
        -- (32 rows affected) update OL Name
update Contracts_NotInCOUPA set OL_supplier_name=o.NAME1 from Contracts_NotInCOUPA c inner join OL_Supplier_Master o on ltrim(rtrim(c.final_supplier_number_new))=ltrim(rtrim(o.VENDOR_ID)) where isnull(c.[Supplier Number],'')<>''
        """,
        """
        -- (513 rows affected)
update Contracts_NotInCOUPA set OL_supplier_name=o.NAME1 from Contracts_NotInCOUPA c inner join OL_Supplier_Master o on ltrim(rtrim(c.Final_Supplier_Name))=ltrim(rtrim(o.NAME1)) where isnull(OL_supplier_name,'')=''
        """,
        """
        -- (21 rows affected)
select * from Contracts_NotInCOUPA where COUPA_Supplier_Status='active' order by [Contract Type Name]
        """,
        """
        -- 171
select * from Contracts_NotInCOUPA where COUPA_Supplier_Status<>'active' order by [Contract Type Name]
        """,
        """
        -- 1138 update final_supp_num_new with number from coupa_supplier where ''
update Contracts_NotInCOUPA set [final_supplier_number_new]=s.[Supplier #] from Contracts_NotInCOUPA c inner join COUPA_Suppliers s on c.[final_supplier_name]=s.Name where isnull([final_supplier_number_new],'')=''
        """,
        """
        -- Inactive Business Users
select distinct c.[Contract #] ,c.[Contract Type Name],o.[Business User*],isnull(u.active,'Not Active') as Active from coupa_contracts c left join [dbo].[Recon_OneLink_Master_New_Union+20240609] o on c.[Contract #]=o.[Contract #] left join coupa_users u on o.[Business User*]=u.[Login] where c.[Contract #] not in (Select distinct [Parent Contract Number] from coupa_contracts where [Hierarchy Type]='Amendment') and c.[Hierarchy Type] In ('Contract','Master') and c.[Contract #] like 'OL%' and u.active is null
        """,
        """
        -- 6,605 Inactive Engagement Users
select distinct c.[Contract #] ,c.[Contract Type Name],o.[Engagement Manager],isnull(u.active,'Not Active') as Active from coupa_contracts c left join [dbo].[Recon_OneLink_Master_New_Union+20240609] o on c.[Contract #]=o.[Contract #] left join coupa_users u on o.[Engagement Manager]=u.[Login] where c.[Contract #] not in (Select distinct [Parent Contract Number] from coupa_contracts where [Hierarchy Type]='Amendment') and c.[Hierarchy Type] In ('Contract','Master') and c.[Contract #] like 'OL%' and u.active is null
        """,
        """
        select distinct c.[Contract #] ,c.[Contract Type Name],o.[Business User*],o.[Engagement Manager] from coupa_contracts c left join [dbo].[Recon_OneLink_Master_New_Union+20240609] o on c.[Contract #]=o.[Contract #] where c.[Contract #] not in (Select distinct [Parent Contract Number] from coupa_contracts where [Hierarchy Type]='Amendment') and c.[Hierarchy Type] In ('Contract','Master') and c.[Contract #] like 'CAH%'
        """,
        """
        -- 1,292 don't do vizient yet.. ask Meena
select * from coupa_contracts where [Contract #] not in (Select distinct [Parent Contract Number] from coupa_contracts where [Hierarchy Type]='Amendment') and [Hierarchy Type] In ('Contract','Master') and [Contract Type Name] IN ('VPA - Vizient Product Agreement','VSA - Vizient Standalone Agreement','VMA - Vizient Master Agreement')
        """,
        """
        -- 754 Active Business Users for load (for OL contracts only, not relevant for Vizient or CAH)
select distinct 'Contract Header' as [Contract Header] ,c.[Contract Name],c.[Contract #],c.[Hierarchy Type] ,o.[Business User*]--,isnull(u.active,'Not Active') as Active from coupa_contracts c left join [dbo].[Recon_OneLink_Master_New_Union+20240609] o on c.[Contract #]=o.[Contract #] left join coupa_users u on o.[Business User*]=u.[Login] where c.[Contract #] not in (Select distinct [Parent Contract Number] from coupa_contracts where [Hierarchy Type]='Amendment') and c.[Hierarchy Type] In ('Contract','Master') and c.[Contract #] like 'OL%' and u.active = 'active' and c.[Business User*]='P529206'
        """,
        """
        -- 4054 524 OL contracts with business user not Angel. DID NOT UPDATE .. NEED TO ASK
select distinct [Contract #],[Business User*] from coupa_contracts where [Contract #] like 'OL_%' and [Business User*]<>'P529206'
        """,
        """
        select * from coupa_users where [Login]='P529206'
        """,
        """
        -- Inactive Engagement Users
select distinct 'Contract Header' as [Contract Header] ,c.[Contract Name],c.[Contract #] ,c.[Hierarchy Type],o.[Engagement Manager]
        """,
        """
        -- ,isnull(u.active,'Not Active') as Active
from coupa_contracts c left join [dbo].[Recon_OneLink_Master_New_Union+20240609] o on c.[Contract #]=o.[Contract #] left join coupa_users u on o.[Engagement Manager]=u.[Login] where c.[Contract #] not in (Select distinct [Parent Contract Number] from coupa_contracts where [Hierarchy Type]='Amendment') and c.[Hierarchy Type] In ('Contract','Master') and c.[Contract #] like 'OL_%' and u.active='active' and c.[Engagement Manager]=''
        """,
        """
        select distinct [Contract #],[Engagement Manager] from coupa_contracts where [Contract #] like 'OL_%' and [Engagement Manager]='P529206' -- 0 engagement managers for angel
        """,
        """
        drop table [CareAtHome_Owner_Update_Load]
        """,
        """
        select *
        """,
        """
        -- into [dbo].[CareAtHome_Owner_Update_Load]
from [dbo].[CareAtHome_Owner_Updates] u --114 where not exists (Select 'X' from coupa_contracts c where c.[Contract #]= ltrim(rtrim(replace(replace(u.[Contract #],'OL','CAH'),'HIC',''))))
        """,
        """
        -- and u.[Contract Type Name] IN  ('NSA - National Supplier Agreement','PPA - Participant Plan Agreement') 49 out of 114
select * from coupa_contracts where [Contract #] like '%2185%'
        """,
        """
        select * from [dbo].[CareAtHome_Owner_Update_Load]
        """,
        """
        select cah.*,c.Name as COUPA_Name,c.Status as COUPA_Status from (select * from [Recon_OneLink_Master_New_Union] u where not exists (Select 'x' from coupa_contracts c where ltrim(rtrim(replace(replace(u.[Contract #],'OL','CAH'),'HIC','')))=c.[Contract #]) and u.[Contract Type Name] IN ('PPA - Participant Plan Agreement','NSA - National Supplier Agreement')) as cah left join COUPA_Suppliers c on cah.[Supplier Number]=c.[Supplier #]
        """,
        """
        select distinct [Contract Type Name],[Contract #] from [Prod_U_2024-04-22_Load] o where not exists (Select 'X' from  [dbo].[Vizient_Payment_Rebates_20240112] v where o.[Contract #]=v.[CurrentContractID])
        """,
        """
        select distinct [Contract Type Name],[Contract #] from [Prod_X_2024-04-19_Load] o where not exists (Select 'X' from  [dbo].[Vizient_Payment_Rebates_20240112] v where o.[Contract #]=v.[CurrentContractID])
        """,
        """
        select distinct [Contract Type Name],[Contract #] from [Prod_T_2024-04-19_Load] o where not exists (Select 'X' from  [dbo].[Vizient_Payment_Rebates_20240112] v where o.[Contract #]=v.[CurrentContractID])
        """,
        """
        -- commodity updates select contracts from coupa with blank commodity (OL contracts)
select distinct 'Contract Header',c.[Contract Name],c.[Contract #],c.[hierarchy type],c.[Commodity Name],o.[Commodity Name] from coupa_contracts c left join OneLink_Master_New o on c.[Contract #]=o.[Contract #] where c.[Contract #] like 'OL%' and c.[Commodity Name]='' and c.[Hierarchy Type] In ('Contract','Master') order by 4
        """,
        """
        -- select contracts from coupa with blank commodity (Care At Home contracts)
select distinct 'Contract Header',[Contract Name],[Contract #],[Contract Type Name],[Commodity Name] from coupa_contracts where [Contract #] like '%CAH%' and [Commodity Name]='' order by 4
        """,
        """
        -- commodity checks
select distinct [Contract #],[Contract Name],[Contract Type Name],[Supplier Number],[Supplier Name],[Starts],[Expires],[Commodity Name],[Description] from coupa_contracts where [Commodity Name] = 'IaaS'
        """,
        """
        select distinct [Contract #],[Contract Name],[Contract Type Name],[Supplier Number],[Supplier Name],[Starts],[Expires],[Commodity Name],[Description] from [dbo].[OneLink_Master_New] where [Commodity Name] = 'Cloud Services'
        """,
        """
        select distinct [Contract #],[Contract Name],[Contract Type Name],[Supplier Number],[Supplier Name],[Starts],[Expires],[Commodity Name],[Description] from [dbo].[OneLink_Master_Delta_Full] where [Commodity Name] ='Cloud Services'
        """,
        """
        Inactivate: Information Technology > Cloud Service Providers > IaaS > AWS Information Technology > Cloud Service Providers > IaaS > Azure Information Technology > Cloud Service Providers > IaaS > GCP Information Technology > Cloud Service Providers > Other Cloud Service Providers Information Technology > Cloud Service Providers > Cloud Services Information Technology > Cloud Service Providers > Cloud Services > System Installation Cloud Services
        """,
        """
        Update to last leaf Node: Information Technology > Cloud Service Providers > IaaS
        """,
        """
        select * from [dbo].[VizientCommodityMapping] where [DESCR60] like '%IaaS%' or [Commodity Name] like '%IaaS%'
        """,
        """
        select distinct [Contract #],[Commodity Name] from coupa_contracts where [Commodity Name] like '%hardware%'
        """,
        """
        -- MSOW validation
Select distinct [External Contract Identifier],[Contract Type Name], Starts, Expires ,[Maximum Spend] ,[Price & Payment Contract Type Custom Field 1],[Price & Payment Contract Type Custom Field 2],[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment sPro Pre-Consumed/FG Consumed amount] from OneLink_Master_New_FG_Load where [Contract Type Name] like 'MSOW%' and [External Contract Identifier] IN ('FG_0000000000000000003248','FG_0000000000000000003477','FG_0000000000000000003478','FG_0000000000000000003479','FG_0000000000000000006479','FG_0000000000000000006709','FG_0000000000000000006998','FG_0000000000000000008258','FG_0000000000000000008613','FG_0000000000000000008629','FG_0000000000000000010258','FG_0000000000000000010989','FG_0000000000000000011460','FG_0000000000000000011690','FG_0000000000000000011740','FG_0000000000000000012123','FG_0000000000000000012664','FG_0000000000000000012686','FG_0000000000000000013316','FG_0000000000000000013331','FG_0000000000000000013341','FG_0000000000000000013367','FG_0000000000000000013368','FG_0000000000000000013369','FG_0000000000000000013371','FG_0000000000000000013372','FG_0000000000000000013373','FG_0000000000000000013374','FG_0000000000000000013376','FG_0000000000000000013386','FG_0000000000000000013387','FG_0000000000000000015374','FG_0000000000000000016173','FG_0000000000000000017390','FG_0000000000000000017765','FG_0000000000000000017767','FG_0000000000000000020406','FG_13366-1','FG_13370-1','FG_13385-1','FG_13387-1','FG_14197-1','FG_184-3576-17058','FG_4117-1','442-1570-13554','FG_4541-5857-15133','674-808-16990','0000000000000000000001893','0000000000000000000002253','0000000000000000000002871','0000000000000000000006404','0000000000000000000008997','0000000000000000000010940','0000000000000000000012968','0000000000000000000013334','0000000000000000000014197','0000000000000000000014712','0000000000000000000017306','0000000000000000000017586','0000000000000000000017702','0000000000000000000017802','0000000000000000000017904','0000000000000000000018322','0000000000000000000018418','0000000000000000000019496','0000000000000000000021063','FG_0000000000000000021278')
        """,
        """
        -- LOA
Select distinct [External Contract Identifier],[Contract Type Name], Starts,Expires ,[Price & Payment Contract Type Custom Field 1],[Price & Payment Contract Type Custom Field 2],[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4],[Price & Payment Contract Type Custom Field 5] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] ,[sPro/Legacy Consumed (paid)] from OneLink_Master_New_FG_Load where [Contract Type Name]= 'LOA - Letter of Agreement' and [External Contract Identifier] IN ('FG_0000000000000000006662','FG_0000000000000000007126','FG_0000000000000000010976','FG_0000000000000000011636','FG_0000000000000000011994','FG_0000000000000000018631','FG_0000000000000000019529','FG_0000000000000000019944','FG_0000000000000000020774','FG_0000000000000000020844','FG_10623R','FG_20774-1','FG-0000000000000000000617','FG-20715','FG_0000000000000000019738','FG_0000000000000000020416','FG_0000000000000000021273','FG_0000000000000000000258','FG_0000000000000000000974','0000000000000000000011012','0000000000000000000011092','0000000000000000000012818','0000000000000000000015927','0000000000000000000016190','0000000000000000000016842','0000000000000000000017056','0000000000000000000017711','0000000000000000000017937','0000000000000000000017946','0000000000000000000018862','0000000000000000000019012','0000000000000000000019382','0000000000000000000019482','0000000000000000000019723','0000000000000000000019767','0000000000000000000019799','0000000000000000000019894','0000000000000000000020973','0000000000000000000021005','0000000000000000000021050','0000000000000000000021051','0000000000000000000021107','0000000000000000000021141','0000000000000000000021147','0000000000000000000021150','0000000000000000000021180','0000000000000000000021184','0000000000000000000021219','0000000000000000000021247','0000000000000000000021261','0000000000000000000021402','0000000000000000000003311','0000000000000000000021455','FG_0000000000000000018945','FG_00000000000000010623R4')
        """,
        """
        -- JO in ('JOB','LOA - Letter of Agreement','SOW - Statement of Work')
Select distinct [External Contract Identifier],[Contract Type Name], Starts,Expires, FG ,[Price & Payment Contract Type Custom Field 1],[Price & Payment Contract Type Custom Field 2],[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4],[Price & Payment Contract Type Custom Field 5] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] ,[sPro/Legacy Consumed (paid)] ,updatedDefaultAccountforSupplierInvoice from OneLink_Master_New_FG_Load where [Contract Type Name]= 'JOB' and [External Contract Identifier] IN ('FG_0000000000000000004600','FG_0000000000000000004785','FG_0000000000000000004843','FG_0000000000000000006200','FG_0000000000000000006266','FG_0000000000000000007439','FG_0000000000000000008624','FG_0000000000000000008820','FG_0000000000000000008871','FG_0000000000000000008972','FG_0000000000000000009168','FG_0000000000000000009227','FG_0000000000000000009521','FG_0000000000000000009744','FG_0000000000000000009749','FG_0000000000000000009752','FG_0000000000000000009900','FG_0000000000000000009901','FG_0000000000000000009952','FG_0000000000000000009979','FG_0000000000000000010065','FG_0000000000000000010084','FG_0000000000000000010159','FG_0000000000000000010491','FG_0000000000000000010587','FG_0000000000000000011125','FG_0000000000000000011480','FG_0000000000000000011764','FG_0000000000000000011804','FG_0000000000000000011866','FG_0000000000000000011869','FG_0000000000000000012066','FG_0000000000000000012121','FG_0000000000000000012230','FG_0000000000000000012245','FG_0000000000000000012353','FG_0000000000000000012355','FG_0000000000000000012621','FG_0000000000000000012650','FG_0000000000000000012651','FG_0000000000000000012730','FG_0000000000000000012749','FG_0000000000000000012752','FG_0000000000000000012803','FG_0000000000000000012806','FG_0000000000000000012822','FG_0000000000000000012874','FG_0000000000000000012875','FG_0000000000000000013050','FG_0000000000000000013104','FG_0000000000000000013137','FG_0000000000000000013179','FG_0000000000000000013437','FG_0000000000000000013480','FG_0000000000000000013482','FG_0000000000000000013483','FG_0000000000000000013484','FG_0000000000000000013493','FG_0000000000000000013494','FG_0000000000000000013495','FG_0000000000000000013496','FG_0000000000000000013504','FG_0000000000000000013509','FG_0000000000000000013510','FG_0000000000000000013524','FG_0000000000000000013526','FG_0000000000000000013527','FG_0000000000000000013528','FG_0000000000000000013530','FG_0000000000000000013531','FG_0000000000000000013532','FG_0000000000000000013535','FG_0000000000000000013537','FG_0000000000000000013551','FG_0000000000000000013564','FG_0000000000000000013565','FG_0000000000000000013566','FG_0000000000000000013567','FG_0000000000000000013568','FG_0000000000000000013569','FG_0000000000000000013570','FG_0000000000000000013571','FG_0000000000000000013573','FG_0000000000000000013580','FG_0000000000000000013583','FG_0000000000000000013605','FG_0000000000000000013633','FG_0000000000000000013636','FG_0000000000000000013700','FG_0000000000000000013703','FG_0000000000000000013704','FG_0000000000000000013705','FG_0000000000000000013860','FG_0000000000000000014061','FG_0000000000000000014771','FG_0000000000000000014896','FG_0000000000000000015410','FG_0000000000000000015593','FG_0000000000000000015632','FG_0000000000000000015633','FG_0000000000000000015634','FG_0000000000000000015714','FG_0000000000000000015857','FG_0000000000000000015861','FG_0000000000000000016099','FG_0000000000000000016280','FG_0000000000000000016457','FG_0000000000000000016598','FG_0000000000000000016660','FG_0000000000000000016670','FG_0000000000000000016672','FG_0000000000000000016746','FG_0000000000000000016815','FG_0000000000000000016840','FG_0000000000000000016897','FG_0000000000000000016910','FG_0000000000000000016911','FG_0000000000000000017033','FG_0000000000000000017144','FG_0000000000000000017381','FG_0000000000000000017434','FG_0000000000000000017516','FG_0000000000000000017521','FG_0000000000000000017534','FG_0000000000000000017537','FG_0000000000000000017549','FG_0000000000000000017612','FG_0000000000000000017621','FG_0000000000000000017628','FG_0000000000000000017685','FG_0000000000000000017686','FG_0000000000000000017691','FG_0000000000000000017692','FG_0000000000000000017701','FG_0000000000000000017893','FG_0000000000000000018094','FG_0000000000000000018095','FG_0000000000000000018104','FG_0000000000000000018145','FG_0000000000000000018189','FG_0000000000000000018191','FG_0000000000000000018239','FG_0000000000000000018285','FG_0000000000000000018409','FG_0000000000000000018416','FG_0000000000000000018421','FG_0000000000000000018518','FG_0000000000000000018666','FG_0000000000000000018674','FG_0000000000000000018687','FG_0000000000000000018711','FG_0000000000000000018782','FG_0000000000000000018815','FG_0000000000000000018989','FG_0000000000000000018991','FG_0000000000000000019016','FG_0000000000000000019158','FG_0000000000000000019159','FG_0000000000000000019161','FG_0000000000000000019162','FG_0000000000000000019163','FG_0000000000000000019181','FG_0000000000000000019184','FG_0000000000000000019185','FG_0000000000000000019186','FG_0000000000000000019187','FG_0000000000000000019188','FG_0000000000000000019310','FG_0000000000000000019317','FG_0000000000000000019356','FG_0000000000000000019366','FG_0000000000000000019372','FG_0000000000000000019405','FG_0000000000000000019463','FG_0000000000000000019483','FG_0000000000000000019487','FG_0000000000000000019564','FG_0000000000000000019580','FG_0000000000000000019587','FG_0000000000000000019633','FG_0000000000000000019646','FG_0000000000000000019749','FG_0000000000000000019773','FG_0000000000000000019835','FG_0000000000000000019850','FG_0000000000000000019958','FG_0000000000000000019966','FG_0000000000000000019995','FG_0000000000000000020094','FG_0000000000000000020280','FG_0000000000000000020282','FG_0000000000000000020285','FG_0000000000000000020286','FG_0000000000000000020289','FG_0000000000000000020290','FG_0000000000000000020298','FG_0000000000000000020311','FG_0000000000000000020328','FG_0000000000000000020331','FG_0000000000000000020341','FG_0000000000000000020350','FG_0000000000000000020402','FG_0000000000000000020408','FG_0000000000000000020409','FG_0000000000000000020428','FG_0000000000000000020440','FG_0000000000000000020456','FG_0000000000000000020462','FG_0000000000000000020488','FG_0000000000000000020546','FG_0000000000000000020589','FG_0000000000000000020613','FG_0000000000000000020616','FG_0000000000000000020625','FG_0000000000000000020626','FG_0000000000000000020627','FG_0000000000000000020628','FG_0000000000000000020632','FG_0000000000000000020668','FG_0000000000000000020678','FG_0000000000000000020691','FG_0000000000000000020692','FG_0000000000000000020696','FG_0000000000000000020701','FG_0000000000000000020707','FG_0000000000000000020708','FG_0000000000000000020723','FG_0000000000000000020726','FG_0000000000000000020747','FG_0000000000000000020756','FG_0000000000000000020792','FG_0000000000000000020888','FG_0000000000000000021310','FG_0000000000000000021311','FG_0000000000000000021312','FG_13607-1','FG_13625-1','FG_13626-1','FG_13634-1','FG_13635-1','FG_13650-1','FG-12296','0000000000000000000011804','0000000000000000000011866','0000000000000000000011869','0000000000000000000012066','0000000000000000000012121','0000000000000000000012128','0000000000000000000012230','0000000000000000000012245','0000000000000000000012296','0000000000000000000012349','0000000000000000000012355','0000000000000000000012489','0000000000000000000012960','0000000000000000000013579','0000000000000000000013612','0000000000000000000013613','0000000000000000000013614','0000000000000000000013621','0000000000000000000013916','0000000000000000000013945','0000000000000000000014135','0000000000000000000014165','0000000000000000000014176','0000000000000000000014562','0000000000000000000001473','0000000000000000000014942','0000000000000000000015281','0000000000000000000017111','0000000000000000000017164','0000000000000000000017322','0000000000000000000017470','0000000000000000000017476','0000000000000000000017525','0000000000000000000017536','0000000000000000000017561','0000000000000000000017671','0000000000000000000017688','0000000000000000000017693','0000000000000000000017700','0000000000000000000017832','0000000000000000000018033','0000000000000000000018081','0000000000000000000018099','0000000000000000000018264','0000000000000000000018363','0000000000000000000018426','0000000000000000000018856','0000000000000000000018858','0000000000000000000018895','0000000000000000000018898','0000000000000000000019018','0000000000000000000019044','0000000000000000000019110','0000000000000000000019160','0000000000000000000019182','0000000000000000000019183','0000000000000000000019272','0000000000000000000019378','0000000000000000000019579','0000000000000000000019627','0000000000000000000019700','0000000000000000000019714','0000000000000000000019786','0000000000000000000019787','0000000000000000000019860','0000000000000000000019883','0000000000000000000019900','0000000000000000000019954','0000000000000000000020021','0000000000000000000020057','0000000000000000000020284','0000000000000000000020353','0000000000000000000020956','0000000000000000000020965','0000000000000000000020976','0000000000000000000020996','0000000000000000000021025','0000000000000000000021027','0000000000000000000021028','0000000000000000000021034','0000000000000000000021038','0000000000000000000021049','0000000000000000000021054','0000000000000000000021055','0000000000000000000021067','0000000000000000000021069','0000000000000000000021075','0000000000000000000021082','0000000000000000000021090','0000000000000000000021092','0000000000000000000021093','0000000000000000000021104','0000000000000000000021105','0000000000000000000021109','0000000000000000000021112','0000000000000000000021113','0000000000000000000021128','0000000000000000000021132','0000000000000000000021136','0000000000000000000021140','0000000000000000000021157','0000000000000000000021182','0000000000000000000021183','0000000000000000000021190','0000000000000000000021213','0000000000000000000021257','0000000000000000000021262','0000000000000000000021276','0000000000000000000021280','0000000000000000000021305','0000000000000000000021306','0000000000000000000021307','0000000000000000000021308','0000000000000000000021309','0000000000000000000021314','0000000000000000000021329','0000000000000000000021358','0000000000000000000021400','14721-1','0000000000000000000013607','0000000000000000000013624','0000000000000000000013625','0000000000000000000013626','0000000000000000000013634','0000000000000000000013635','0000000000000000000013650','0000000000000000000017369','0000000000000000000020102','0000000000000000000020705','0000000000000000000020870')
        """,
        """
        -- SOW
Select distinct [External Contract Identifier],[Contract Type Name], Starts,Expires, FG ,[Price & Payment Contract Type Custom Field 1],[Price & Payment Contract Type Custom Field 2],[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4],[Price & Payment Contract Type Custom Field 5] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] ,[sPro/Legacy Consumed (paid)] ,updatedDefaultAccountforSupplierInvoice from OneLink_Master_New_FG_Load where [Contract Type Name] like 'SOW%' and [External Contract Identifier] IN ('FG_0000000000000000001698','FG_0000000000000000002689','FG_0000000000000000002875','FG_0000000000000000002924','FG_0000000000000000003095','FG_0000000000000000005604','FG_0000000000000000006128','FG_0000000000000000006131','FG_0000000000000000006162','FG_0000000000000000006163','FG_0000000000000000006389','FG_0000000000000000006390','FG_0000000000000000006391','FG_0000000000000000006392','FG_0000000000000000006393','FG_0000000000000000006427','FG_0000000000000000006399','FG_0000000000000000006401','FG_0000000000000000009013','FG_0000000000000000006131','FG_0000000000000000002734','FG_0000000000000000005604','FG_0000000000000000009018','FG_0000000000000000009019','FG_0000000000000000010378','FG_0000000000000000012172','FG_0000000000000000012433','FG_0000000000000000013184','FG_0000000000000000013233','FG_0000000000000000013427','FG_0000000000000000013963','FG_0000000000000000013975','FG_0000000000000000014718','FG_0000000000000000015349','FG_0000000000000000015419','FG_0000000000000000015502','FG_0000000000000000015515','FG_0000000000000000015946','FG_0000000000000000016045','FG_0000000000000000016046','FG_0000000000000000016174','FG_0000000000000000016188','FG_0000000000000000016212','FG_0000000000000000016240','FG_0000000000000000016382','FG_0000000000000000016441','FG_0000000000000000017215','FG_0000000000000000017230','FG_0000000000000000017291','FG_0000000000000000017533','FG_0000000000000000017570','FG_0000000000000000017533','FG_0000000000000000017579','FG_0000000000000000017599','FG_0000000000000000018671','FG_0000000000000000018695','FG_0000000000000000018747','FG_0000000000000000019419','FG_0000000000000000019820','FG_0000000000000000019824','FG_0000000000000000020002','FG_0000000000000000020072','FG_0000000000000000020076','FG_0000000000000000020294','FG_0000000000000000020307','FG_0000000000000000020476','FG_0000000000000000020515','FG_0000000000000000020544','FG_0000000000000000020561','FG_0000000000000000020574','FG_0000000000000000020580','FG_0000000000000000020637','FG_0000000000000000020682','FG_0000000000000000020772','FG_0000000000000000020806','FG_0000000000000000020818','FG_0000000000000000020864','FG_0000000000000000020877','FG_0000000000000000020929','FG_0000000000000000020935','FG_0000000000000000021186','FG_0000000000000000021188','FG_0000000000000000021256','FG_0000000000000000021258','FG_0000000000000000021317','FG_0000000000000000021330','FG_18004-R','FG_21129','FG-20938','FG_21178','FG_R-00000000000000020770','FG-0000000000000000015192','FG-18198','FG_0000000000000000006174','FG_0000000000000000006433','FG_0000000000000000006434','FG_0000000000000000006435','FG_0000000000000000006436','FG_0000000000000000006437','FG_0000000000000000006440','FG_0000000000000000006442','FG_0000000000000000006443','FG_0000000000000000006444','FG_0000000000000000006445','FG_0000000000000000006446','FG_0000000000000000006447','FG_0000000000000000006448','FG_0000000000000000006449','FG_0000000000000000006450','FG_0000000000000000006451','FG_0000000000000000006452','FG_0000000000000000006453','FG_0000000000000000006454','FG_0000000000000000006455','FG_0000000000000000006456','FG_0000000000000000006495','FG_0000000000000000006672','FG_0000000000000000006765','FG_0000000000000000006767','FG_0000000000000000006770','FG_0000000000000000006771','FG_0000000000000000006772','FG_0000000000000000006773','FG_0000000000000000006775','FG_0000000000000000006777','FG_0000000000000000007307','FG_0000000000000000008409','FG_0000000000000000008570','FG_0000000000000000008638','FG_0000000000000000008663','FG_0000000000000000008916','FG_0000000000000000009006','FG_0000000000000000009007','FG_0000000000000000009538','FG_0000000000000000009606','FG_0000000000000000009803','FG_0000000000000000009861','FG_0000000000000000010503','FG_0000000000000000010749','FG_0000000000000000010834','FG_0000000000000000010868','FG_0000000000000000010919','FG_0000000000000000011006','FG_0000000000000000011218','FG_0000000000000000011220','FG_0000000000000000011287','FG_0000000000000000011479','FG_0000000000000000011661','FG_0000000000000000011722','FG_0000000000000000011723','FG_0000000000000000011783','FG_0000000000000000011787','FG_0000000000000000012119','FG_0000000000000000012161','FG_0000000000000000012283','FG_0000000000000000012412','FG_0000000000000000012418','FG_0000000000000000012452','FG_0000000000000000012525','FG_0000000000000000012609','FG_0000000000000000012823','FG_0000000000000000013234','FG_0000000000000000013245','FG_0000000000000000013301','FG_0000000000000000013302','FG_0000000000000000013307','FG_0000000000000000013505','FG_0000000000000000013644','FG_0000000000000000013663','FG_0000000000000000014134','FG_0000000000000000014148','FG_0000000000000000014269','FG_0000000000000000014371','FG_0000000000000000014395','FG_0000000000000000014476','FG_0000000000000000014640','FG_0000000000000000014924','FG_0000000000000000015021','FG_0000000000000000015050','FG_0000000000000000015301','FG_0000000000000000015310','FG_0000000000000000015329','FG_0000000000000000015334','FG_0000000000000000015408','FG_0000000000000000015413','FG_0000000000000000015424','FG_0000000000000000015446','FG_0000000000000000015508','FG_0000000000000000015554','FG_0000000000000000015680','FG_0000000000000000015720','FG_0000000000000000015952','FG_0000000000000000016047','FG_0000000000000000016079','FG_0000000000000000016223','FG_0000000000000000016554','FG_0000000000000000016608','FG_0000000000000000016783','FG_0000000000000000017224','FG_0000000000000000017226','FG_0000000000000000017228','FG_0000000000000000017236','FG_0000000000000000017237','FG_0000000000000000017305','FG_0000000000000000017350','FG_0000000000000000017378','FG_0000000000000000017384','FG_0000000000000000017385','FG_0000000000000000017423','FG_0000000000000000017440','FG_0000000000000000017502','FG_0000000000000000017515','FG_0000000000000000017529','FG_0000000000000000017623','FG_0000000000000000017661','FG_0000000000000000017678','FG_0000000000000000017697','FG_0000000000000000017759','FG_0000000000000000017818','FG_0000000000000000017820','FG_0000000000000000017855','FG_0000000000000000017904','FG_0000000000000000017922','FG_0000000000000000018016','FG_0000000000000000018119','FG_0000000000000000018137','FG_0000000000000000018147','FG_0000000000000000018166','FG_0000000000000000018194','FG_0000000000000000018262','FG_0000000000000000018283','FG_0000000000000000018320','FG_0000000000000000018337','FG_0000000000000000018388','FG_0000000000000000018418','FG_0000000000000000018525','FG_0000000000000000018548','FG_0000000000000000018556','FG_0000000000000000018583','FG_0000000000000000018616','FG_0000000000000000018619','FG_0000000000000000018640','FG_0000000000000000018688','FG_0000000000000000018697','FG_0000000000000000018721','FG_0000000000000000018722','FG_0000000000000000018733','FG_0000000000000000018775','FG_0000000000000000018835','FG_0000000000000000018874','FG_0000000000000000018879','FG_0000000000000000018917','FG_0000000000000000018946','FG_0000000000000000018999','FG_0000000000000000019051','FG_0000000000000000019130','FG_0000000000000000019246','FG_0000000000000000019248','FG_0000000000000000019255','FG_0000000000000000019318','FG_0000000000000000019329','FG_0000000000000000019337','FG_0000000000000000019401','FG_0000000000000000019573','FG_0000000000000000019609','FG_0000000000000000019639','FG_0000000000000000019662','FG_0000000000000000019669','FG_0000000000000000019699','FG_0000000000000000019715','FG_0000000000000000019724','FG_0000000000000000019732','FG_0000000000000000019760','FG_0000000000000000019761','FG_0000000000000000019861','FG_0000000000000000019869','FG_0000000000000000019870','FG_0000000000000000019881','FG_0000000000000000019888','FG_0000000000000000019940','FG_0000000000000000019969','FG_0000000000000000020018','FG_0000000000000000020027','FG_0000000000000000020028','FG_0000000000000000020048','FG_0000000000000000020052','FG_0000000000000000020056','FG_0000000000000000020067','FG_0000000000000000020086','FG_0000000000000000020088','FG_0000000000000000020104','FG_0000000000000000020105','FG_0000000000000000020109','FG_0000000000000000020119','FG_0000000000000000020134','FG_0000000000000000020150','FG_0000000000000000020155','FG_0000000000000000020156','FG_0000000000000000020161','FG_0000000000000000020163','FG_0000000000000000020168','FG_0000000000000000020199','FG_0000000000000000020221','FG_0000000000000000020264','FG_0000000000000000020267','FG_0000000000000000020295','FG_0000000000000000020308','FG_0000000000000000020309','FG_0000000000000000020310','FG_0000000000000000020317','FG_0000000000000000020332','FG_0000000000000000020335','FG_0000000000000000020336','FG_0000000000000000020337','FG_0000000000000000020339','FG_0000000000000000020340','FG_0000000000000000020342','FG_0000000000000000020344','FG_0000000000000000020345','FG_0000000000000000020355','FG_0000000000000000020357','FG_0000000000000000020370','FG_0000000000000000020371','FG_0000000000000000020412','FG_0000000000000000020422','FG_0000000000000000020423','FG_0000000000000000020424','FG_0000000000000000020425','FG_0000000000000000020454','FG_0000000000000000020455','FG_0000000000000000020457','FG_0000000000000000020466','FG_0000000000000000020467','FG_0000000000000000020474','FG_0000000000000000020506','FG_0000000000000000020523','FG_0000000000000000020543','FG_0000000000000000020555','FG_0000000000000000020559','FG_0000000000000000020575','FG_0000000000000000020587','FG_0000000000000000020599','FG_0000000000000000020615','FG_0000000000000000020635','FG_0000000000000000020652','FG_0000000000000000020660','FG_0000000000000000020665','FG_0000000000000000020679','FG_0000000000000000020684','FG_0000000000000000020688','FG_0000000000000000020693','FG_0000000000000000020698','FG_0000000000000000020699','FG_0000000000000000020709','FG_0000000000000000020714','FG_0000000000000000020722','FG_0000000000000000020730','FG_0000000000000000020750','FG_0000000000000000020770','FG_0000000000000000020780','FG_0000000000000000020790','FG_0000000000000000020793','FG_0000000000000000020799','FG_0000000000000000020860','FG_0000000000000000020861','FG_0000000000000000020863','FG_0000000000000000020865','FG_0000000000000000020920','FG_0000000000000000020921','FG_000000000000000011981','FG_674-808-14736','FG_974-2394-17108','FG_12767-R','FG_14019-1','FG_14350-1','FG_15843-1','FG_16819-1','FG_16900-R','FG_17818-1','FG_18478-1','FG_19284-1','FG_20266','FG_20838','FG_20947','FG_21035','FG_CNTR0013122_3R','FG_PS-13175_1','FG00000000000000000019628','FG-11913','FG-18460','FG-19300','FG-19726','0000000000000000000010499','0000000000000000000011913','0000000000000000000012315','0000000000000000000012598','0000000000000000000012767','0000000000000000000013142','0000000000000000000013314','0000000000000000000013651','0000000000000000000013737','0000000000000000000013817','0000000000000000000014019','0000000000000000000014156','0000000000000000000014319','0000000000000000000014596','0000000000000000000001500','0000000000000000000015009','0000000000000000000015319','0000000000000000000015383','0000000000000000000015418','0000000000000000000015442','0000000000000000000015448','0000000000000000000015547','0000000000000000000015561','0000000000000000000015643','0000000000000000000015871','0000000000000000000015906','0000000000000000000015976','0000000000000000000015982','0000000000000000000015983','0000000000000000000015984','0000000000000000000015988','0000000000000000000015995','0000000000000000000015996','0000000000000000000015998','0000000000000000000016000','0000000000000000000016017','0000000000000000000016041','0000000000000000000016153','0000000000000000000016164','0000000000000000000016210','0000000000000000000016289','0000000000000000000016361','0000000000000000000016427','0000000000000000000016432','0000000000000000000016524','0000000000000000000016553','0000000000000000000016607','0000000000000000000016665','0000000000000000000016747','0000000000000000000016763','0000000000000000000016770','0000000000000000000016791','0000000000000000000016852','16900-R','0000000000000000000016902','0000000000000000000016931','0000000000000000000017042','0000000000000000000017049','0000000000000000000017090','0000000000000000000017153','0000000000000000000017155','0000000000000000000017179','0000000000000000000017253','0000000000000000000017275','0000000000000000000017282','17400-R','17572R','0000000000000000000017632','0000000000000000000017662','17696-R','0000000000000000000017738','0000000000000000000017783','0000000000000000000017877','0000000000000000000017907','0000000000000000000017932','0000000000000000000017963','0000000000000000000018172','0000000000000000000018213','0000000000000000000018245','0000000000000000000018246','0000000000000000000018313','18332-R','18332-R-1','0000000000000000000018365','0000000000000000000018366','0000000000000000000018396','18396-A','0000000000000000000018469','0000000000000000000018527','0000000000000000000018546','0000000000000000000018550','0000000000000000000018684','0000000000000000000018698','0000000000000000000018705','0000000000000000000018725','0000000000000000000018848','0000000000000000000018903','0000000000000000000018920','0000000000000000000018924','0000000000000000000018975','0000000000000000000018993','0000000000000000000018996','0000000000000000000018998','0000000000000000000019001','0000000000000000000019201','0000000000000000000019220','0000000000000000000019244','0000000000000000000019250','0000000000000000000019264','0000000000000000000019284','0000000000000000000019297','0000000000000000000019335','0000000000000000000019343','0000000000000000000019360','0000000000000000000019363','0000000000000000000019371','0000000000000000000019416','19453R','0000000000000000000019513','0000000000000000000019517','0000000000000000000019551','0000000000000000000019644','0000000000000000000019649','0000000000000000000019670','0000000000000000000019762','0000000000000000000019814','0000000000000000000019815','0000000000000000000019822','0000000000000000000019876','0000000000000000000019888','0000000000000000000019972','0000000000000000000019975','0000000000000000000019990','0000000000000000000019991','0000000000000000000020002','0000000000000000000020005','0000000000000000000020012','0000000000000000000020071','0000000000000000000020100','0000000000000000000020107','0000000000000000000020121','0000000000000000000020144','0000000000000000000020151','0000000000000000000020164','0000000000000000000020166','0000000000000000000020178','0000000000000000000020180','0000000000000000000020201','0000000000000000000020202','0000000000000000000020326','0000000000000000000020332','0000000000000000000020334','0000000000000000000020338','0000000000000000000020365','0000000000000000000020413','0000000000000000000020429','0000000000000000000020500','0000000000000000000020505','0000000000000000000020509','0000000000000000000020510','0000000000000000000020511','0000000000000000000020540','0000000000000000000020563','0000000000000000000020800','0000000000000000000020801','0000000000000000000020806','0000000000000000000020890','0000000000000000000020893','0000000000000000000020932','0000000000000000000020937','0000000000000000000020939','0000000000000000000020952','0000000000000000000020955','0000000000000000000020958','0000000000000000000020963','0000000000000000000020969','0000000000000000000020974','0000000000000000000020975','0000000000000000000020985','0000000000000000000020986','0000000000000000000020990','0000000000000000000020993','0000000000000000000020995','0000000000000000000020998','0000000000000000000021000','0000000000000000000021008','0000000000000000000021009','0000000000000000000021010','0000000000000000000021016','0000000000000000000021018','0000000000000000000021019','0000000000000000000021023','0000000000000000000021026','0000000000000000000021029','0000000000000000000021031','0000000000000000000021036','0000000000000000000021045','0000000000000000000021047','0000000000000000000021048','0000000000000000000021058','0000000000000000000021060','0000000000000000000021061','0000000000000000000021062','0000000000000000000021064','0000000000000000000021065','0000000000000000000021066','0000000000000000000021068','0000000000000000000021070','0000000000000000000021073','0000000000000000000021074','0000000000000000000021083','0000000000000000000021084','0000000000000000000021086','0000000000000000000021089','0000000000000000000021091','0000000000000000000021094','0000000000000000000021097','0000000000000000000021098','0000000000000000000021101','0000000000000000000021102','0000000000000000000021106','0000000000000000000021117','0000000000000000000021121','0000000000000000000021131','0000000000000000000021133','0000000000000000000021134','0000000000000000000021135','0000000000000000000021138','0000000000000000000021139','0000000000000000000021143','0000000000000000000021144','0000000000000000000021145','0000000000000000000021146','0000000000000000000021148','0000000000000000000021149','0000000000000000000021152','0000000000000000000021153','0000000000000000000021154','0000000000000000000021159','0000000000000000000021161','0000000000000000000021164','0000000000000000000021168','0000000000000000000021169','0000000000000000000021170','0000000000000000000021171','0000000000000000000021172','0000000000000000000021173','0000000000000000000021174','0000000000000000000021176','0000000000000000000021187','0000000000000000000021192','0000000000000000000021197','0000000000000000000021198','0000000000000000000021201','0000000000000000000021216','0000000000000000000021220','0000000000000000000021225','0000000000000000000021233','0000000000000000000021234','0000000000000000000021238','0000000000000000000021239','0000000000000000000021240','0000000000000000000021242','0000000000000000000021243','0000000000000000000021244','0000000000000000000021246','0000000000000000000021248','0000000000000000000021249','0000000000000000000021250','0000000000000000000021251','0000000000000000000021254','0000000000000000000021259','0000000000000000000021264','0000000000000000000021265','0000000000000000000021266','0000000000000000000021267','0000000000000000000021268','0000000000000000000021269','0000000000000000000021271','0000000000000000000021272','0000000000000000000021274','0000000000000000000021275','0000000000000000000021277','0000000000000000000021281','0000000000000000000021285','0000000000000000000021288','0000000000000000000021290','0000000000000000000021291','0000000000000000000021292','0000000000000000000021293','0000000000000000000021294','0000000000000000000021295','0000000000000000000021296','0000000000000000000021297','0000000000000000000021298','0000000000000000000021299','0000000000000000000021301','0000000000000000000021303','0000000000000000000021304','0000000000000000000021315','0000000000000000000021320','0000000000000000000021321','0000000000000000000021322','0000000000000000000021323','0000000000000000000021324','0000000000000000000021325','0000000000000000000021326','0000000000000000000021327','0000000000000000000021328','0000000000000000000021331','0000000000000000000021332','0000000000000000000021333','0000000000000000000021335','0000000000000000000021338','0000000000000000000021339','0000000000000000000021340','0000000000000000000021341','0000000000000000000021342','0000000000000000000021343','0000000000000000000021345','0000000000000000000021346','0000000000000000000021347','0000000000000000000021348','0000000000000000000021349','0000000000000000000021350','0000000000000000000021351','0000000000000000000021352','0000000000000000000021356','0000000000000000000021357','0000000000000000000021361','0000000000000000000021362','0000000000000000000021363','0000000000000000000021364','0000000000000000000021365','0000000000000000000021366','0000000000000000000021367','0000000000000000000021369','0000000000000000000021370','0000000000000000000021371','0000000000000000000021372','0000000000000000000021373','0000000000000000000021374','0000000000000000000021375','0000000000000000000021376','0000000000000000000021377','0000000000000000000021378','0000000000000000000021379','0000000000000000000021380','0000000000000000000021381','0000000000000000000021382','0000000000000000000021394','0000000000000000000021397','0000000000000000000021398','0000000000000000000021399','0000000000000000000021401','0000000000000000000021403','0000000000000000000021404','0000000000000000000021405','0000000000000000000021406','0000000000000000000021407','0000000000000000000021414','0000000000000000000021415','0000000000000000000021419','0000000000000000000021420','0000000000000000000021421','0000000000000000000021424','0000000000000000000021425','0000000000000000000021428','0000000000000000000021429','0000000000000000000021430','0000000000000000000021434','0000000000000000000021438','0000000000000000000021439','0000000000000000000021440','0000000000000000000021441','0000000000000000000021445','0000000000000000000021447','0000000000000000000021451','0000000000000000000002179','0000000000000000000002756','0000000000000000000002876','0000000000000000000004863','0000000000000000000005142','0000000000000000000005146','0000000000000000000005636','0000000000000000000005658','6159R','0000000000000000000006181','0000000000000000000006401','0000000000000000000007516','0000000000000000000007639','0000000000000000000007658','0000000000000000000007660','0000000000000000000007661','0000000000000000000007663','0000000000000000000007678','0000000000000000000007685','0000000000000000000007687','0000000000000000000007688','0000000000000000000007691','0000000000000000000007692','0000000000000000000007705','0000000000000000000007706','0000000000000000000007707','0000000000000000000007708','0000000000000000000007718','0000000000000000000007722','0000000000000000000007724','0000000000000000000007727','0000000000000000000007733','0000000000000000000007738','0000000000000000000007750','0000000000000000000007752','0000000000000000000007753','0000000000000000000007754','0000000000000000000007755','0000000000000000000007764','0000000000000000000007767','0000000000000000000007771','0000000000000000000007775','0000000000000000000007776','0000000000000000000007792','0000000000000000000007803','0000000000000000000007805','0000000000000000000007807','0000000000000000000007810','0000000000000000000007811','0000000000000000000007815','0000000000000000000007829','0000000000000000000007832','0000000000000000000007833','0000000000000000000007836','0000000000000000000007839','0000000000000000000007842','0000000000000000000007843','0000000000000000000007844','0000000000000000000007854','0000000000000000000007855','0000000000000000000007858','0000000000000000000007862','0000000000000000000007877','0000000000000000000007883','0000000000000000000007886','0000000000000000000007919','0000000000000000000007920','0000000000000000000007964','0000000000000000000007965','0000000000000000000008548','0000000000000000000008588','0000000000000000000008688','0000000000000000000008945','0000000000000000000009003','0000000000000000000009040','9491R','9493R','0000000000000000000009647','11604-1','14297-1','16781-1','17818-1','19264-1','20443-1','344-9249','674-808-14736','PS-13175_1')
        """,
        """
        select distinct [Contract Type Name] from coupa_contracts
        """,
        """
        select * from coupa_contracts where [Contract Type Name]='Punchout'
        """,
        """
        select * from coupa_uat_suppliers where name like '%sAFEGUARD%'
        """,
        """
        Inspired     SAFEGUARD BUSINESS SYSTEMS INC	100046497	active Markmaster   MARKMASTER INC	100014010	active Office Depot OFFICE DEPOT INC	100027599	active Office Relief OFFICE RELIEF INC	100014003	active Rittenhouse  RITTENHOUSE BOOK DISTRIBUTORS INC  100015787	active Scan Technology Inc 100027441	active SHI INTERNATIONAL CORP  100023511	active Sycomp SYCOMP A TECHNOLOGY COMPANY INC	100204128	active Veritiv VERITIV OPERATING COMPANY	100011153	active
        """,
        """
        select 'Contract Header' as [Contract Header], 'Punchout: AMAZON CAPITAL SERVICES INC' as [Contract Name],'' AS [Contract #],'Contract' as [Hierarchy Type] ,'' as [Parent Contract Number],'' as [Parent Contract Name],'' as [Supplier Name],'100160269' as [Supplier Number],'2024-10-16' as Starts,'' as Expires ,'Draft' as Status,'' as [Legal Agreement],'USD' as [Currency],'' as [Source],'' as [Supplier Account #],'P529206' as [Owner Login],'' as [Default On Unbacked Lines] ,'' as [Supplier Can Invoice Directly] ,'' as [Default Account Type for Supplier Invoice] ,'' as [Default Account for Supplier Invoice] ,'' as [Savings %] ,'' as [Minimum Spend] ,'' as [Maximum Spend] ,'No' as [Stop Spend Over Contract Value] ,'Everyone' as [Content Groups] ,'No' as [Use Order Windows] ,'' as [Payment Terms] ,'' as [Shipping Terms] ,'Anytime' as [Order Windows Sunday] ,'Anytime' as [Order Windows Monday] ,'Anytime' as [Order Windows Tuesday] ,'Anytime' as [Order Windows Wednesday] ,'Anytime' as [Order Windows Thursday] ,'Anytime' as [Order Windows Friday] ,'Anytime' as [Order Windows Saturday] ,'' as [Order Windows Timezone] ,'' as [Order Windows PO Message] ,'' as [Order Windows Requisition Message] ,'' as [Attachment 1] ,'' as [Attachment 2] ,'' as [Attachment 3] ,'' as [Attachment 4] ,'' as [Attachment 5] ,'' as [Attachment 6] ,'' as [Attachment 7] ,'' as [Attachment 8] ,'' as [Attachment 9] ,'' as [Attachment 10] ,'' as [Termination Notice] ,'Perpetual' as [Term Type] ,'No' as [Terminated] ,'' as [Termination Reason Code] ,'' as [Termination Reason Comment] ,'' as [Consent to Assignment] ,'Yes' as [Used For Buying] ,'No' as [Automatically update expiry date] ,'' as [No of Renewals] ,'Days' as [Renewal Length(Unit)] ,'' as [Renewal Length(Value)] ,'Days' as [Length of Notice(Unit)] ,'' as [Length of Notice(value)] ,'' as [Termination Notice Length(Unit)] ,'' as [Termination Notice Length(Value)] ,'' as [Description] ,'' as [Published Date] ,'' as [Execution Date] ,'' as [Department Name] ,'Punchout' as [Contract Type Name] ,'' as [Contract Type Custom Field 1] ,'' as [Contract Type Custom Field 2] ,'' as [Contract Type Custom Field 3] ,'' as [Contract Type Custom Field 4] ,'' as [Contract Type Custom Field 5] ,'' as [Contract Type Custom Field 6] ,'' as [Contract Type Custom Field 7] ,'' as [Contract Type Custom Field 8] ,'' as [Contract Type Custom Field 9] ,'' as [Contract Type Custom Field 10] ,'No' as [Strict Invoicing Rules] ,'' as [E-Signature Account] ,'' as [External Contract Identifier] ,'Buy-Side' as [Contract Classification] ,'Not Specified' [Whose Paper] ,'' as [Alternate Dispute Resolution] ,'' as [Governing Law Country Region Code] ,'' as [Jurisdiction Country Region Code] ,'' as [Governing Law State] ,'' as [Jurisdiction State] ,'' as [Jurisdiction Exclusivity] ,'' as [Nondisclosure Copying Restriction] ,'No' as [Permitted Disclosees Directors] ,'No' as [Permitted Disclosees Employees] ,'No' as [Permitted Disclosees Advisers] ,'No' as [Permitted Disclosees Contractors] ,'' as [Notice Methods] ,'' as [Contract Details Contract Type Custom Field 1] ,'' as [Contract Details Contract Type Custom Field 2] ,'' as [Contract Details Contract Type Custom Field 3] ,'' as [Contract Details Contract Type Custom Field 4] ,'' as [Contract Details Contract Type Custom Field 5] ,'' as [Parties Contract Type Custom Field 1] ,'' as [Parties Contract Type Custom Field 2] ,'' as [Parties Contract Type Custom Field 3] ,'' as [Parties Contract Type Custom Field 4] ,'' as [Parties Contract Type Custom Field 5] ,'' as [Term & Renewal Contract Type Custom Field 1] ,'' as [Term & Renewal Contract Type Custom Field 2] ,'' as [Term & Renewal Contract Type Custom Field 3] ,'' as [Term & Renewal Contract Type Custom Field 4] ,'' as [Term & Renewal Contract Type Custom Field 5] ,'' as [Termination Contract Type Custom Field 1] ,'' as [Termination Contract Type Custom Field 2] ,'' as [Termination Contract Type Custom Field 3] ,'' as [Termination Contract Type Custom Field 4] ,'' as [Termination Contract Type Custom Field 5] ,'' as [Performance Contract Type Custom Field 1] ,'' as [Performance Contract Type Custom Field 2] ,'' as [Performance Contract Type Custom Field 3] ,'' as [Performance Contract Type Custom Field 4] ,'' as [Performance Contract Type Custom Field 5] ,'' as [Price & Payment Contract Type Custom Field 1] ,'' as [Price & Payment Contract Type Custom Field 2] ,'' as [Price & Payment Contract Type Custom Field 3] ,'' as [Price & Payment Contract Type Custom Field 4] ,'' as [Price & Payment Contract Type Custom Field 5] ,'' as [Dispute & Remedies Contract Type Custom Field 1] ,'' as [Dispute & Remedies Contract Type Custom Field 2] ,'' as [Dispute & Remedies Contract Type Custom Field 3] ,'' as [Dispute & Remedies Contract Type Custom Field 4] ,'' as [Dispute & Remedies Contract Type Custom Field 5] ,'' as [Risk Contract Type Custom Field 1] ,'' as [Risk Contract Type Custom Field 2] ,'' as [Risk Contract Type Custom Field 3] ,'' as [Risk Contract Type Custom Field 4] ,'' as [Risk Contract Type Custom Field 5] ,'' as [IP & Data Contract Type Custom Field 1] ,'' as [IP & Data Contract Type Custom Field 2] ,'' as [IP & Data Contract Type Custom Field 3] ,'' as [IP & Data Contract Type Custom Field 4] ,'' as [IP & Data Contract Type Custom Field 5] ,'' as [Relationship & Reporting Contract Type Custom Field 1] ,'' as [Relationship & Reporting Contract Type Custom Field 2] ,'' as [Relationship & Reporting Contract Type Custom Field 3] ,'' as [Relationship & Reporting Contract Type Custom Field 4] ,'' as [Relationship & Reporting Contract Type Custom Field 5] ,'P529206' as [Business User*] ,'' as [Engagement Type] ,'' as [Engagement Manager] ,'' as [Region Code Service Area] ,'' as [Offshore Service Addendum Required?] ,'' as [Countries of Operation] ,'' as [Commodity Name] ,'' as [Parties Line of Business] ,'' as [Parties Other LOB] ,'' as [Price & Payment Estimated Spend] ,'' as [Price & Payment Early Payment Discount Terms] ,'' as [Price & Payment Rebates]
        """,
        """
        select distinct e.[CNTRCT_ID],e.[VENDOR_ID],e.[NAME1],e.[VENDOR_STATUS],e.[CNTRCT_STATUS],e.[CNTRCT_BEGIN_DT],e.[CNTRCT_EXPIRE_DT] , case [KP_RQST_TYPE2] when 'A' then 'MSA - Master Services Agreement' when 'B' then 'MSOW - Master Statement of Work' when 'D' then 'SOW - Statement of Work' when 'G' then 'LOA - Letter of Agreement' WHEN 'H' THEN 'NSA - National Supplier Agreement' WHEN 'I' THEN 'BAA - Business Associate Agreement' WHEN 'K' THEN 'NDA - Mutual Non-Disclosure Agreement' WHEN 'L' THEN 'PPA - Participant Plan Agreement' WHEN 'M' THEN 'Services Agreement' WHEN 'N' THEN 'SEA - Single Entity Agreement' WHEN 'O' THEN 'SWLA - Software License Agreement' WHEN 'P' THEN 'TECH - Technology Evaluation Agreement' WHEN 'R' THEN 'JOB' WHEN 'S' THEN 'MPRODS - Master Products/Services Agreement' WHEN 'T' THEN 'VPA - Vizient Product Agreement' WHEN 'U' THEN 'VSA - Vizient Standalone Agreement' WHEN 'V' THEN 'DSA - Data Sharing Agreement' WHEN 'W' THEN 'EQUIPMA - Equipment Maintenanc' WHEN 'X' THEN 'VMA - Vizient Master Agreement' WHEN 'Y' THEN 'ConSignA - Consignment Agreement' WHEN 'Z' THEN 'VOF - Vendor Order Form' else [KP_RQST_TYPE2] end , c.Status  as COUPA_Status,sum(cast(s.[SPEND] as float)) as Spend from [dbo].[Expired contract From Meena] e left join COUPA_Suppliers c on e.[VENDOR_ID]=c.[Supplier #] left join [dbo].[expired_contract_spend] s on e.[VENDOR_ID]=s.[INV_SUPPLIER_ID] group by e.[CNTRCT_ID],e.[VENDOR_ID],e.[NAME1],e.[VENDOR_STATUS],e.[CNTRCT_STATUS],e.[CNTRCT_BEGIN_DT],e.[CNTRCT_EXPIRE_DT],[KP_RQST_TYPE2] ,c.Status
        """,
        """
        select distinct [KP_RQST_TYPE2] from [dbo].[Expired contract From Meena] order by 1
        """,
        """
        select * from [dbo].[Expired contract From Meena] where [KP_RQST_TYPE2]='1'
        """,
        """
        select distinct [Contract Type Name],[Contract #] from [dbo].[OneLink_ExpiredContracts_Master] where filename is null
        """,
        """
        select distinct [Contract Type Name],[Contract #] from [dbo].[OneLink_ExpiredContracts_Master] where [Contract Type Name] like 'Consign%' order by 2
        """,
        """
        select distinct [Contract Type Name] from [OneLink_ExpiredContracts_Master_LOAD_PROD] select distinct [Contract Type Name] from [OneLink_ExpiredContracts_Master_LOADED_PROD]
        """,
        """
        select distinct * from [OneLink_ExpiredContracts_Master_LOAD_PROD]
        """,
        """
        -- now check for supplier availability in COUPA
drop table [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD]
        """,
        """
        -- move loaded contracts to load table insert into [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD]
select * into [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] from [dbo].[OneLink_ExpiredContracts_Master] e where not exists (Select 'x' from [OneLink_ExpiredContracts_Master_ALL_NotLoaded] n where e.[Contract #]=n.[Contract #]) and e.[Contract Type Name] ='VSA - Vizient Standalone Agreement'
        """,
        """
        -- (3962 MSA rows affected) (3083 LOA rows affected) 763 SA (449 rows affected) SWLA (1104 MSA rows affected) later 469 equip 103 tech 96 SEA 504 VSA
alter table  [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] add updatedCommodityName nvarchar(255); alter table  [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] add updatedEngagementManager nvarchar(255); alter table  [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] add updatedBusinessUser nvarchar(255); alter table  [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] add UpdatedDefaultAccountforSupplierInvoice nvarchar(255);
        """,
        """
        -- extraction for PROD business users, engagement managers if business user is active, else update with what Angel per Wendy if engagement managers is active, use as is else blank  [Business User*] updating to angel when blank
update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set updatedBusinessUser=[Business User*];
        """,
        """
        -- update to Angel
update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set updatedBusinessUser='P529206' from [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] e where not exists (Select 'x' from [dbo].[coupa_users] u where e.[Business User*]=u.Login and u.Active='Active');
        """,
        """
        -- (10 rows affected) [Engagement Manager]
update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set updatedEngagementManager=[Engagement Manager];
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set updatedEngagementManager='' from [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] e where  not exists (Select 'x' from [dbo].[coupa_users] u where e.[Engagement Manager]=u.Login and u.Active='Active');
        """,
        """
        -- hierarchy type?? tie to an MSA for an SOW else use as is category update (use the old one)
update [OneLink_ExpiredContracts_Master_LOAD_PROD] set UpdatedCommodityName=case c.[Replacement Commodity Name] when '' then c.[Commodity Name] else c.[Replacement Commodity Name] end from [OneLink_ExpiredContracts_Master_LOAD_PROD] u inner join [dbo].[VizientCommodityMapping] c on substring(u.[Commodity Name],len(left(u.[Commodity Name],charindex('-',u.[Commodity Name])))+1,len(u.[Commodity Name]))=c.[DESCR60]
        """,
        """
        select distinct [Commodity Name],substring([Commodity Name],len(left([Commodity Name],charindex('-',[Commodity Name])))+1,len([Commodity Name])) ,UpdatedCommodityName from [OneLink_ExpiredContracts_Master_LOAD_PROD] where UpdatedCommodityName is null
        """,
        """
        -- custom commodity updates if needed
update [OneLink_ExpiredContracts_Master_LOAD_PROD] set UpdatedCommodityName='Bed, Stretcher and Patient Equipment' where [Commodity Name]='10553-Bed  Stretcher and Patent Care';
        """,
        """
        update [OneLink_ExpiredContracts_Master_LOAD_PROD] set UpdatedCommodityName='Housekeeping Uniforms, Gowns and Linens' where [Commodity Name]='10449-Housekeeping Uniform Gown&Linens';
        """,
        """
        update [OneLink_ExpiredContracts_Master_LOAD_PROD] set UpdatedCommodityName='Heating, Ventilating and Air Conditioning - HVAC' where [Commodity Name]='10490-Heating  Ventilating and Air Conditioning (HVAC)';
        """,
        """
        update [OneLink_ExpiredContracts_Master_LOAD_PROD] set UpdatedCommodityName='Parking, Valet and Shuttle Services' where [Commodity Name]='10502-Parking  Valet and Shuttle Services';
        """,
        """
        update [OneLink_ExpiredContracts_Master_LOAD_PROD] set UpdatedCommodityName='Move, Add, Change - MAC' where [Commodity Name]='10491-Move  Add  Change (MAC)';
        """,
        """
        -- Vizient specific updates
alter table [OneLink_ExpiredContracts_Master_LOAD_PROD] add  [Parties KP Legal Entity] nvarchar(255); alter table [OneLink_ExpiredContracts_Master_LOAD_PROD] add [Financial Commitment] nvarchar(255);
        """,
        """
        -- 5. update contract type custom fields
update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N';
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y';
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N';
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y';
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N';
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y';
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N';
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y';
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select * --distinct [Contract Type Custom Field 8] from [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] where [Contract Type Custom Field 8]='';
        """,
        """
        -- ****there is a blank in 1 contract.. CHECK WITH MEENA Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
update [dbo].[OneLink_ExpiredContracts_Master_LOAD_PROD] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO';
        """,
        """
        -- Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        /**
        """,
        """
        -- check GLString (ignore gl string for now.. REX working on it)
Select distinct [Contract #],[Default Account for Supplier Invoice] from [OneLink_ExpiredContracts_Master_LOAD_PROD] order by 1
        """,
        """
        update [OneLink_ExpiredContracts_Master_LOAD_PROD] set UpdatedDefaultAccountforSupplierInvoice=m.[Concatenated_Result] from [OneLink_ExpiredContracts_Master_LOAD_PROD] e inner join [dbo].[FG_GLLookUp_Master] m on e.[Default Account for Supplier Invoice]=m.[Default Account for Supplier Invoice] **/
        """,
        """
        update [OneLink_ExpiredContracts_Master_LOAD_PROD] set UpdatedDefaultAccountforSupplierInvoice='';
        """,
        """
        -- only for MSA update [OneLink_ExpiredContracts_Master_LOAD_PROD] set Expires='2061-01-01'
select distinct [Contract #] from [OneLink_ExpiredContracts_Master_LOAD_PROD] order by 1
        """,
        """
        select distinct [Contract #] from OneLink_ExpiredContracts_Master where [Contract Type Name] like 'MSA%' order by 1
        """,
        """
        select * from
        """,
        """
        -- look at not loaded to fix folders
Select distinct [Contract Type Name],[Contract #],[Reason for Not Loaded] from [OneLink_ExpiredContracts_Master_ALL_NotLoaded]
        """,
        """
        Select distinct [Contract Type Name],[Contract #]--,Expires from [OneLink_ExpiredContracts_Master_LOAD_PROD] --where [Contract #]='OL_CID_3815-8647' order by 1,2
        """,
        """
        update [OneLink_ExpiredContracts_Master_LOAD_PROD] set expires='2024-07-31' where [Contract #]='OL_CID_3815-8647'
        """,
        """
        -- 7/31/24 export for Prod load
select [Contract Header] ,[Contract Name] ,[Contract #] ,[Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[final_supplier] as [Supplier Number]  -- I was not using this before so some contracts may have failed on supplier!!! DUMB!! ,[Starts] ,Expires--,'2061-01-01' as [Expires] MSA Only ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,finalOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,'' as [Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,[Contract Type Custom Field 1] ,[Contract Type Custom Field 2] ,[Contract Type Custom Field 3] ,[Contract Type Custom Field 4] ,[Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,[Price & Payment Contract Type Custom Field 1] ,[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,[UpdatedBusinessUser] as [Business User*] ,[Engagement Type] ,updatedEngagementManager as [Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,isnull(updatedcommodityname,'') as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] from [OneLink_ExpiredContracts_Master_LOAD_PROD] where [Contract #] IN ('') order by [Contract #]
        """,
        """
        -- Vizient export for Prod load
select [Contract Header] ,[Contract Name] ,[Contract #] ,[Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[final_supplier] as [Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,finalOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,[Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,[Contract Type Custom Field 1] ,[Contract Type Custom Field 2] ,[Contract Type Custom Field 3] ,[Contract Type Custom Field 4] ,[Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,[Price & Payment Contract Type Custom Field 1] ,[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,[UpdatedBusinessUser] as [Business User*] ,[Engagement Type] ,updatedEngagementManager as [Engagement Manager] ,[Region Code Service Area] ,'No' as [Offshore Service Addendum Required?] ,[Countries of Operation] ,case when updatedcommodityname like '%,%' then '"'+isnull(updatedcommodityname,'')+'"' else isnull(updatedcommodityname,'') end as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'' as [Parties KP Legal Entity] ,'NOFCR' as [Financial Commitment] from [OneLink_ExpiredContracts_Master_LOAD_PROD] where [Contract #] in ('BM04158','BM11135','BM11988','BM12392','BM12753','BM13270','BM13444','BM13693','BM15108','BM15981','BM16035','BM16044','BM16066','BM16072','BM16085','BM16087','BM16089','BM16095','BM16110','BM16126','BM16128','BM16135','BM16137','BM16164','BM16167','BM16169','BM16286','BM16289','BM16402','BM16530','BM16542','BM16544','BM18035','BM19211','BM19213','BM19218','BM19219','BM19233','BM19235') order by [Contract #]
        """,
        """
        select distinct [Contract Type Name],[Contract #] from [OneLink_ExpiredContracts_Master_LOAD_PROD] order by 2
        """,
        """
        select * into [OneLink_ExpiredContracts_Master_LOADED_PROD_bk_DSA_ConSign_NDA] from [OneLink_ExpiredContracts_Master_LOADED_PROD]
        """,
        """
        drop table [OneLink_ExpiredContracts_Master_LOADED_PROD]
        """,
        """
        -- move loaded contracts to loaded table
insert into [OneLink_ExpiredContracts_Master_LOADED_PROD] select *
        """,
        """
        -- into [OneLink_ExpiredContracts_Master_LOADED_PROD]
from [OneLink_ExpiredContracts_Master_LOAD_PROD]
        """,
        """
        -- 227
select distinct [Contract Type Name] from [OneLink_ExpiredContracts_Master_LOAD_PROD] select distinct [Contract Type Name] from [OneLink_ExpiredContracts_Master_LOADED_PROD] where  [Contract Type Name] like 'MSA%'
        """,
        """
        -- export MSA's to update expiry dates
select 'Contract Header' as [Contract Header], [Contract Name],[Contract #],[Hierarchy Type],Expires from [OneLink_ExpiredContracts_Master] m where  exists (Select 'x' from [OneLink_ExpiredContracts_Master_LOADED_UAT] l where m.[Contract #]=l.[Contract #]) and [Contract Type Name] like 'MSA%'
        """,
        """
        select distinct [Contract Type Name],[Contract #] from [dbo].[OneLink_ExpiredContracts_Master] where filename is null
        """,
        """
        select distinct [Contract Type Name],[Contract #] from [dbo].[OneLink_ExpiredContracts_Master] where [Contract Type Name] like 'ConSignA%' order by 2
        """,
        """
        -- replacement supplier
update [dbo].[OneLink_ExpiredContracts_Master] set replacement_supplier = s.[Replacement ID] from [dbo].[OneLink_ExpiredContracts_Master] e inner join [dbo].[ReplacementVendors20240408] s on e.[Supplier Number]=s.Vendor_Id
        """,
        """
        -- 161 update final supplier number
update [dbo].[OneLink_ExpiredContracts_Master] set [final_supplier]= case when isnull(replacement_supplier,'')=''  then [Supplier Number] else replacement_supplier end
        """,
        """
        -- (6029 rows affected)
select distinct [Supplier Number],replacement_supplier,final_supplier from [OneLink_ExpiredContracts_Master]
        """,
        """
        -- now check for supplier availability in COUPA drop table [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] move loaded contracts to load table insert into [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT]
select * into [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] from [dbo].[OneLink_ExpiredContracts_Master] e where exists (Select 'x' from [dbo].[COUPA_uat_Suppliers] s where e.final_supplier=s.[Supplier #]) and e.[Contract #] in ('OL_4243','OL_4244','OL_4245','OL_4320','OL_4321','OL_4807','OL_4828','OL_5190','OL_5192','OL_5193')
        """,
        """
        -- ('OL_0000005116','OL_0000007546','OL_0000011130','OL_0000011488','OL_0000013237','OL_0000013325','OL_0000015650','OL_0000016347','OL_0000017086','OL_03-10248_SRO') and e.[Contract Type Name] like 'MSA%' (16 rows affected)
alter table  [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] add updatedCommodityName nvarchar(255); alter table  [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] add updatedOwnerLogin nvarchar(255); alter table  [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] add updatedEngagementManager nvarchar(255); alter table  [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] add updatedBusinessUser nvarchar(255); alter table  [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] add UpdatedDefaultAccountforSupplierInvoice nvarchar(255);
        """,
        """
        select * from [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] order by [Contract #]
        """,
        """
        -- extraction for UAT owner login, business users, engagement managers uat - angel owner login list if business user is active, else update with what Bill/Wendy approves if engagement managers is active, use as is else blank Owner Login
select distinct [Owner Login] from [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] e where not exists (Select 'x' from [dbo].[coupa_users] u where e.[Owner Login]=u.Login) /** I317836 O014646 O743970 **/ update [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] set updatedOwnerLogin=[Owner Login]
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] set updatedOwnerLogin='P529206'
        """,
        """
        -- where updatedOwnerLogin IN ('I317836','O014646','O743970') [Business User*]
select distinct [Business User*] from [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] e where not exists (Select 'x' from [dbo].[coupa_users] u where e.[Business User*]=u.Login) /** B463759 M803720 O743970 **/
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] set updatedBusinessUser=[Business User*]
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] set updatedBusinessUser='P529206'
        """,
        """
        -- where updatedBusinessUser in ('B463759','M803720','O743970') [Engagement Manager]
select distinct [Engagement Manager] from [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] e where not exists (Select 'x' from [dbo].[coupa_users] u where e.[Engagement Manager]=u.Login) /** A739497 M803720**/
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] set updatedEngagementManager=[Engagement Manager]
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] set updatedEngagementManager='' from [dbo].[OneLink_ExpiredContracts_Master_LOAD_UAT] e where  not exists (Select 'x' from [dbo].[coupa_users] u where e.[Engagement Manager]=u.Login)
        """,
        """
        -- hierarchy type?? tie to an MSA for an SOW else use as is category update (use the old one)
select distinct [Commodity Name],substring([Commodity Name],len(left([Commodity Name],charindex('-',[Commodity Name])))+1,len([Commodity Name])) ,UpdatedCommodityName from OneLink_ExpiredContracts_Master_LOAD_UAT
        """,
        """
        update OneLink_ExpiredContracts_Master_LOAD_UAT set UpdatedCommodityName=case c.[Replacement Commodity Name] when '' then c.[Commodity Name] else c.[Replacement Commodity Name] end from OneLink_ExpiredContracts_Master_LOAD_UAT u inner join [dbo].[VizientCommodityMapping] c on substring(u.[Commodity Name],len(left(u.[Commodity Name],charindex('-',u.[Commodity Name])))+1,len(u.[Commodity Name]))=c.[DESCR60]
        """,
        """
        -- check GLString
Select distinct [Contract #]--,[Default Account for Supplier Invoice] from OneLink_ExpiredContracts_Master_LOAD_UAT order by 1
        """,
        """
        update OneLink_ExpiredContracts_Master_LOAD_UAT set UpdatedDefaultAccountforSupplierInvoice=m.[Concatenated_Result] from OneLink_ExpiredContracts_Master_LOAD_UAT e inner join [dbo].[FG_GLLookUp_Master] m on e.[Default Account for Supplier Invoice]=m.[Default Account for Supplier Invoice]
        """,
        """
        update OneLink_ExpiredContracts_Master_LOAD_UAT set UpdatedDefaultAccountforSupplierInvoice=''
        """,
        """
        -- only for MSA update OneLink_ExpiredContracts_Master_LOAD_UAT set Expires='2061-01-01'
select distinct expires from OneLink_ExpiredContracts_Master_LOAD_UAT
        """,
        """
        -- export for UAT load
select [Contract Header] ,[Contract Name] ,[Contract #] ,[Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,[UpdatedOwnerLogin] as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,'' as [Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,[Contract Type Custom Field 1] ,[Contract Type Custom Field 2] ,[Contract Type Custom Field 3] ,[Contract Type Custom Field 4] ,[Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,[Price & Payment Contract Type Custom Field 1] ,[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,[UpdatedBusinessUser] as [Business User*] ,[Engagement Type] ,[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,updatedcommodityname as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] from [OneLink_ExpiredContracts_Master_LOAD_UAT]
        """,
        """
        -- where [Contract Type Name] like 'MSA%'
order by [Contract #]
        """,
        """
        select distinct filename,[Contract Type Name],count([Contract #]) from [OneLink_ExpiredContracts_Master_LOAD_UAT] group by filename,[Contract Type Name] order by 1,2
        """,
        """
        -- move loaded contracts to loaded table
insert into [OneLink_ExpiredContracts_Master_LOADED_UAT] select * from [OneLink_ExpiredContracts_Master_LOAD_UAT] where [Contract Type Name] like 'SOW%'
        """,
        """
        delete from [OneLink_ExpiredContracts_Master_LOAD_UAT] where  [Contract Type Name] like 'SOW%'
        """,
        """
        -- export MSA's to update expiry dates
select 'Contract Header' as [Contract Header], [Contract Name],[Contract #],[Hierarchy Type],Expires from [OneLink_ExpiredContracts_Master] m where  exists (Select 'x' from [OneLink_ExpiredContracts_Master_LOADED_UAT] l where m.[Contract #]=l.[Contract #]) and [Contract Type Name] like 'MSA%'
        """,
        """
        select distinct [Contract Type Name],filename,count(distinct [Contract #]) from [dbo].[OneLink_ExpiredContracts_Master] group by [Contract Type Name],filename
        """,
        """
        delete from [dbo].[OneLink_ExpiredContracts_Master] where filename is null
        """,
        """
        delete from [dbo].[OneLink_ExpiredContracts_Master] where [Contract Header] in ('Contract Party','Contract Party Contact')
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='V_2024-08-26.csv' where [Contract Type Name] like 'DSA%'
        """,
        """
        -- (8 rows affected)
update [dbo].[OneLink_ExpiredContracts_Master] set filename='BAA_2024-08-26' --'I_2024-08-26.csv' where [Contract Type Name] like 'BAA%' and isnull(filename,'') =''
        """,
        """
        -- (10 rows affected) -- (135 rows affected)
update [dbo].[OneLink_ExpiredContracts_Master] set filename='A_2024-08-27.csv' where [Contract Type Name] like 'MSA%'
        """,
        """
        -- (1453 rows affected)
update [dbo].[OneLink_ExpiredContracts_Master] set filename='Y_2024-08-26.csv' where [Contract Type Name] like 'ConSignA%'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='B_2024-09-17.csv' where [Contract Type Name] like 'MSOW%'
        """,
        """
        -- 60
update [dbo].[OneLink_ExpiredContracts_Master] set filename='D_2024-09-17.csv' where [Contract Type Name] like 'SOW%'
        """,
        """
        -- (4136 rows affected)
update [dbo].[OneLink_ExpiredContracts_Master] set filename='K_2024-09-04.csv' where [Contract Type Name] like 'NDA%'
        """,
        """
        -- (7 rows affected)
update [dbo].[OneLink_ExpiredContracts_Master] set filename='G_2024-08-26.csv' where [Contract Type Name]='LOA - Letter of Agreement'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='H_2024-09-04.csv' where [Contract Type Name]='NSA - National Supplier Agreement'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='L_2024-09-04.csv' where [Contract Type Name]='PPA - Participant Plan Agreement'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='W_2024-08-26.csv' where [Contract Type Name]='EQUIPMA - Equipment Maintenanc'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='M_2024-09-04.csv' where [Contract Type Name]='Services Agreement'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='N_2024-09-04.csv' where [Contract Type Name]='SEA - Single Entity Agreement'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='NDA_2024-09-04.csv' where [Contract Type Name] like 'NDA%' and filename is null
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='O_2024-09-04.csv' where [Contract Type Name] like 'SWLA%'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='P_2024-09-05.csv' where [Contract Type Name] like 'TECH%'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='S_2024-08-27.csv' where [Contract Type Name] like 'MPRODS%'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='T_2024-09-05.csv' where [Contract Type Name] like 'VPA%'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='U_2024-09-05.csv' where [Contract Type Name] like 'VSA%'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='X_2024-09-05.csv' where [Contract Type Name] like 'vma%'
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set filename='Z_2024-09-05.csv' where [Contract Type Name] like 'vof%'
        """,
        """
        -- Supplier Updates replacement supplier
update [dbo].[OneLink_ExpiredContracts_Master] set replacement_supplier = s.[ReplacementVendorID] from [dbo].[OneLink_ExpiredContracts_Master] e inner join [dbo].[ReplacementVendors] s on e.[Supplier Number]=s.[Vendor Id]
        """,
        """
        -- 297 update final supplier number
update [dbo].[OneLink_ExpiredContracts_Master] set [final_supplier]= case when isnull(replacement_supplier,'')=''  then [Supplier Number] else replacement_supplier end
        """,
        """
        -- (6029 rows affected) load replacement User file
select * from replacementUsers delete from replacementUsers where [Replacement ID] ='N/A'--=''
        """,
        """
        delete from replacementUsers where [Replacement ID]=[Old Owner Login] --252
        """,
        """
        -- gather expired contracts that cannot be loaded apply replacement user to owner login owner logins
alter table  [dbo].[OneLink_ExpiredContracts_Master] add updatedOwnerLogin nvarchar(255); alter table  [dbo].[OneLink_ExpiredContracts_Master] add finalOwnerLogin nvarchar(255);
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set updatedOwnerLogin=null
        """,
        """
        update [dbo].[OneLink_ExpiredContracts_Master] set updatedOwnerLogin=ltrim(rtrim(u.[Replacement ID])) from [dbo].[OneLink_ExpiredContracts_Master] e inner join replacementUsers u on ltrim(rtrim(e.[Owner Login]))=ltrim(rtrim(u.[Old Owner Login]))
        """,
        """
        -- (4833 rows affected)
update [dbo].[OneLink_ExpiredContracts_Master] set finalOwnerLogin= case when isnull(updatedOwnerLogin,'')='' then [Owner Login] else updatedOwnerLogin end
        """,
        """
        select distinct [Owner Login],updatedOwnerLogin,finalOwnerLogin from [OneLink_ExpiredContracts_Master]
        """,
        """
        -- load all contracts whose supplier or users do not exists into another table for reference
drop table [OneLink_ExpiredContracts_Master_Supplier_NotLoaded]
        """,
        """
        Select *,'Supplier' as [Reason for Not Loaded] into  [dbo].[OneLink_ExpiredContracts_Master_Supplier_NotLoaded] from [dbo].[OneLink_ExpiredContracts_Master] e where not exists (Select 'x' from [dbo].[COUPA_Suppliers] s where e.final_supplier=s.[Supplier Number] and s.Status='active')
        """,
        """
        -- (1931 rows affected) drop table [OneLink_ExpiredContracts_Master_OwnerLogins_NotLoaded] load all contracts whose owner logins do not exist into another table for reference
Select *,'Owner Login' as [Reason for Not Loaded] into  [dbo].[OneLink_ExpiredContracts_Master_OwnerLogins_NotLoaded] from [dbo].[OneLink_ExpiredContracts_Master] e where not exists (Select 'x' from [dbo].[coupa_users] u where e.finalOwnerLogin=u.Login and u.[Active]='active')
        """,
        """
        -- (251 rows affected) Create one table so all  issue is in one table
drop table [OneLink_ExpiredContracts_Master_ALL_NotLoaded] select * into [dbo].[OneLink_ExpiredContracts_Master_ALL_NotLoaded] from [dbo].[OneLink_ExpiredContracts_Master_OwnerLogins_NotLoaded]
        """,
        """
        -- (251 rows affected)
alter table [OneLink_ExpiredContracts_Master_ALL_NotLoaded] alter column [Reason for Not Loaded] nvarchar(255)
        """,
        """
        -- add contracts with supplier issues as well
update [OneLink_ExpiredContracts_Master_ALL_NotLoaded] set [Reason for Not Loaded]=e2.[Reason for Not Loaded]+'|'+'Supplier' from [OneLink_ExpiredContracts_Master_Supplier_NotLoaded] e1 inner join [dbo].[OneLink_ExpiredContracts_Master_ALL_NotLoaded] e2 on e1.[Contract #]=e2.[Contract #]
        """,
        """
        -- (23 rows affected) insert missing
insert into [OneLink_ExpiredContracts_Master_ALL_NotLoaded] select * from [OneLink_ExpiredContracts_Master_Supplier_NotLoaded] e1 where not exists (Select 'x' from [dbo].[OneLink_ExpiredContracts_Master_ALL_NotLoaded] e2 where e1.[Contract #]=e2.[Contract #])
        """,
        """
        -- (1908 rows affected)
select * from [dbo].[OneLink_ExpiredContracts_Master]
        """,
        """
        -- 13,650
select distinct * from [OneLink_ExpiredContracts_Master_ALL_NotLoaded]
        """,
        """
        -- 2,159 get owner logins issues
select distinct [Contract #],[Contract Name],[Contract Type Name],e.[Supplier Number],s.Name as COUPA_Supplier_Name,Starts,Expires,[Commodity Name],[Reason for Not Loaded] ,finalOwnerLogin as ReplacedNUID,u1.[Full Name] as ReplacedUserName,u1.Active as ReplacedUserStatus,[Owner Login] as OldNUID,u2.[Full Name] as OldUserName,u2.Active as OldUserStatus from [OneLink_ExpiredContracts_Master_ALL_NotLoaded] e left join COUPA_Suppliers s on e.final_supplier=s.[Supplier Number] left join [dbo].[coupa_users] u1 on e.finalOwnerLogin=u1.Login left join [dbo].[coupa_users] u2 on e.[Owner Login]=u2.Login where [Reason for Not Loaded] in ('Owner Login','Owner Login|Supplier')
        """,
        """
        select * from coupa_users where login='K726421'
        """,
        """
        select * from replacementUsers where [Old Owner Login]='X829218'
        """,
        """
        select [Contract Type Name],[Contract #] from [OneLink_ExpiredContracts_Master_ALL_NotLoaded] where [Contract Type Name] like '%LOA%'
        """,
        """
        group by [Contract Type Name] order by 1
        """,
        """
        select * from [dbo].[OneLink_ExpiredContracts_Master] a where not exists (Select 'X' from [OneLink_ExpiredContracts_Master_ALL_NotLoaded] b where a.[Contract #]=b.[Contract #])
        """,
        """
        -- 11,568
select * from [dbo].[OneLink_ExpiredContracts_Master] where filename ='G_2024-08-26.csv' and [Contract #]='OL_14517'
        """,
        """
        -- 4131
select * from [OneLink_ExpiredContracts_Master_ALL_NotLoaded] where [Contract Type Name] like '%MSA%'
        """,
        """
        -- consumption update
Select 'Contract Header' as [Contract Header],[Contract Name],[External Contract Identifier] as [contract #],[Hierarchy Type]
        """,
        """
        -- ,[Price & Payment Contract Type Custom Field 1],[Price & Payment Contract Type Custom Field 2],[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4],[Price & Payment Contract Type Custom Field 5] ,isnull([sPro/Legacy Consumed (paid)],0) as [Price & Payment sPro Pre-Consumed/FG Consumed amount
,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from OneLink_Master_New_FG_Load where [External Contract Identifier] IN ('0000000000000000000020973','0000000000000000000021005','0000000000000000000021050','0000000000000000000021051','0000000000000000000021107','0000000000000000000021141','0000000000000000000021147','0000000000000000000021150','0000000000000000000021219','0000000000000000000021247','0000000000000000000021402','0000000000000000000021455','FG-0000000000000000000617','FG-20715','FG_0000000000000000000258','FG_0000000000000000000974','FG_0000000000000000006662','FG_0000000000000000010976','FG_0000000000000000011636','FG_0000000000000000011994','FG_0000000000000000018631','FG_0000000000000000018945','FG_0000000000000000019529','FG_0000000000000000019738','FG_0000000000000000019944','FG_0000000000000000020416','FG_0000000000000000020844','FG_0000000000000000021273','FG_00000000000000010623R4','FG_20774-1')
        """,
        """
        select distinct filename from [dbo].[OneLink_Master_New_FG_Delta_20241014]
        """,
        """
        delete from [dbo].[OneLink_Master_New_FG_Delta_20241014] where [Contract Name] IN ('Contract Party Name','Contact Name')
        """,
        """
        delete from [dbo].[OneLink_Master_New_FG_Delta_20241018] where [Contract Name] IN ('Contract Party Name','Contact Name')
        """,
        """
        delete from [dbo].[OneLink_Master_New_FG_Delta_20241025] where [Contract Name] IN ('Contract Party Name','Contact Name')
        """,
        """
        alter table [OneLink_Master_New_FG_Delta_20241018] add filename nvarchar(255)
        """,
        """
        update [OneLink_Master_New_FG_Delta_20241014] set filename='B_2024-10-14'
        """,
        """
        -- 5
update [OneLink_Master_New_FG_Delta_20241018] set filename='B_2024-10-18'
        """,
        """
        -- 2
update [OneLink_Master_New_FG_Delta_20241014] set filename='G_2024-10-14' where filename is null
        """,
        """
        -- 3
update [OneLink_Master_New_FG_Delta_20241014] set filename='R_2024-10-14' where filename is null
        """,
        """
        update [OneLink_Master_New_FG_Delta_20241018] set filename='R_2024-10-18' where filename is null
        """,
        """
        update [OneLink_Master_New_FG_Delta_20241014] set filename='D_2024-10-14' where filename is null
        """,
        """
        update [OneLink_Master_New_FG_Delta_20241018] set filename='D_2024-10-18' where filename is null
        """,
        """
        update [OneLink_Master_New_FG_Delta_20241025] set filename='B_2024-10-25' where filename is null
        """,
        """
        -- (3 rows affected)
update [OneLink_Master_New_FG_Delta_20241025] set filename='R_2024-10-25' where filename is null
        """,
        """
        update [OneLink_Master_New_FG_Delta_20241025] set filename='D_2024-10-25' where filename is null
        """,
        """
        -- custom field population
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW
        """,
        """
        select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_RELEASED] from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d pivot ( max([AMT_LINE_RELEASED]) for [DESCR60] in ([sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        select distinct [DESCR60] from [dbo].FG_AdditionalInformation_FGEnabledSuppliers
        """,
        """
        -- Non-MSOW
select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX] from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee] ,[sPro/Legacy Consumed (paid),[Fixed Fee/Manage Service]) ) piv;
        """,
        """
        select DISTINCT [Contract Type Name] from [dbo].[OneLink_Master_New_FG_Load]
        """,
        """
        select DISTINCT [Contract Type Name] from [dbo].[OneLink_Master_New_FG_Delta]
        """,
        """
        -- insert JO into Load table
insert into [OneLink_Master_New_FG_Load] Select *, null,'Non-FG' from OneLink_Master_New_FG where [Contract Type Name]='JOB'
        """,
        """
        -- 562 work out deltas delta processing (remove old contract and load delta)
Select * from [dbo].[OneLink_Master_New_FG_Delta] where [Contract Type Name]='JOB'
        """,
        """
        -- 241 delete from orig if exists in delta
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta]) and [Contract Type Name]='JOB'
        """,
        """
        -- (206 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select *, null,'Non-FG' from [dbo].[OneLink_Master_New_FG_Delta] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='JOB'
        """,
        """
        -- (241 rows affected) 10/14 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241014]) and [Contract Type Name]='JOB'
        """,
        """
        -- (16 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select *,null,'Non-FG',null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241014] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='JOB'
        """,
        """
        -- (24 rows affected) 10/18 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241018]) and [Contract Type Name]='JOB'
        """,
        """
        -- (4 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select * ,null,'Non-FG',null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241018] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='JOB'
        """,
        """
        -- (4 rows affected) 10/25 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241025]) and [Contract Type Name]='JOB'
        """,
        """
        -- (3 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select * ,null,'Non-FG',null,null,null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241025] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='JOB'
        """,
        """
        -- (4 rows affected) update users owner login updates update owner logins with replacement
update OneLink_Master_New_FG_LOAD set updatedOwnerLogin=[Owner Login]
        """,
        """
        -- 2091
update OneLink_Master_New_FG_LOAD set updatedOwnerLogin=[Replacement ID] from OneLink_Master_New_FG_LOAD f inner join replacementUsers u on ltrim(rtrim(f.[Owner Login]))=ltrim(rtrim(u.[Old Owner Login]))
        """,
        """
        -- (355 rows affected) Business User
update [dbo].OneLink_Master_New_FG_LOAD set updatedBusinessUser=[Business User*];
        """,
        """
        -- 2083 update to Angel when inactive
update [dbo].OneLink_Master_New_FG_LOAD set updatedBusinessUser='P529206' from [dbo].OneLink_Master_New_FG_LOAD e where not exists (Select 'x' from [dbo].[coupa_users] u where e.[Business User*]=u.Login and u.Active='Active');
        """,
        """
        -- (70 rows affected) [Engagement Manager]
update [dbo].OneLink_Master_New_FG_LOAD set updatedEngagementManager=[Engagement Manager];
        """,
        """
        -- (2091 rows affected)
update [dbo].OneLink_Master_New_FG_LOAD set updatedEngagementManager='' from [dbo].OneLink_Master_New_FG_LOAD e where  not exists (Select 'x' from [dbo].[coupa_users] u where e.[Engagement Manager]=u.Login and u.Active='Active');
        """,
        """
        -- (246 rows affected) update FG flag for FG suppliers
update [OneLink_Master_New_FG_Load] set FG='FG' where ltrim(rtrim([Supplier Number])) in (Select ltrim(rtrim([VENDOR_ID])) from FG_EnabledSuppliers) and [Contract Type Name]='JOB'
        """,
        """
        -- (594 rows affected)
select distinct FG from [OneLink_Master_New_FG_Load]
        """,
        """
        select distinct [External Contract Identifier],[Contract #] from [OneLink_Master_New_FG_Load] where [Contract Type Name]='JOB' and FG='Non-FG'
        """,
        """
        -- Only 11 update consumption fields to null before applying latest consumption
update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]=null ,[Price & Payment Contract Type Custom Field 2]=null ,[Price & Payment Contract Type Custom Field 3]=null ,[Price & Payment Contract Type Custom Field 4]=null ,[Price & Payment Contract Type Custom Field 5]=null ,[sPro/Legacy Consumed (paid)] = null;
        """,
        """
        update [OneLink_Master_New_FG_Load] set consumed_fixedfeeManagedService=null ,consumed_TimeandMaterial_managedTeams=null ,consumed_expenses=null ,consumed_programfee=null;
        """,
        """
        -- prep load contract file csv with active status for loading JO only (R file) -- AmtLineMax
drop table [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX]
        """,
        """
        -- from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d
from  [dbo].[FG Consumption data Oct26_filtered])d --[dbo].[FG_MSOW-JO-1018])d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee],[sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        -- (877 rows affected) JO Only -- Consumed Amt
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_RELEASED]
        """,
        """
        -- from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d
from  [dbo].[FG Consumption data Oct26_filtered])d --from [dbo].[FG_MSOW-JO-1018])d pivot ( max([AMT_LINE_RELEASED]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses, [Program Fee]) ) piv;
        """,
        """
        -- (877 rows affected)
alter table [OneLink_Master_New_FG_Load] add [sPro/Legacy Consumed (paid)] nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_expenses nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_programfee nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_TimeandMaterial_managedTeams nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_fixedfeeManagedService nvarchar(255)
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Fixed Fee/Manage Service] ,[Price & Payment Contract Type Custom Field 2]=a.[Time & Material / Managed Teams] ,[Price & Payment Contract Type Custom Field 3]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] ,[Price & Payment Contract Type Custom Field 5]=a.[Program Fee] ,[sPro/Legacy Consumed (paid)] = a.[sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB] a on l.[External Contract Identifier]=a.[CNTRCT_ID] where l.[Contract Type Name]='JOB'
        """,
        """
        -- (290 rows affected)
update [OneLink_Master_New_FG_Load] set consumed_fixedfeeManagedService=a.[Fixed Fee/Manage Service] ,consumed_TimeandMaterial_managedTeams=a.[Time & Material / Managed Teams] ,consumed_expenses=a.[Expenses] ,consumed_programfee=a.[Program Fee] from [OneLink_Master_New_FG_Load] l inner join FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB a--[dbo].FG_AdditionalInformation_FGEnabledSuppliers_Consumed_JOB a on l.[External Contract Identifier]=a.[CNTRCT_ID] where l.[Contract Type Name]='JOB'
        """,
        """
        -- (290 rows affected)
update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]='0' where [Price & Payment Contract Type Custom Field 1]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 2]='0' where [Price & Payment Contract Type Custom Field 2]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 3]='0' where [Price & Payment Contract Type Custom Field 3]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 4]='0' where [Price & Payment Contract Type Custom Field 4]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 5]='0' where [Price & Payment Contract Type Custom Field 5]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]='0' where [Price & Payment Contract Type Custom Field 1] is null ;--'NULL';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 2]='0' where [Price & Payment Contract Type Custom Field 2] is null ;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 3]='0' where [Price & Payment Contract Type Custom Field 3] is null ;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 4]='0' where [Price & Payment Contract Type Custom Field 4] is null ;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 5]='0' where [Price & Payment Contract Type Custom Field 5] is null ;
        """,
        """
        select distinct [Price & Payment Contract Type Custom Field 1] from [OneLink_Master_New_FG_Load]
        """,
        """
        -- gl string make sure load table has cleansed [Default Account for Supplier Invoice] so we can join to accounts table properly
update [dbo].[OneLink_Master_New_FG_Load] set cleansedDefaultAccountforSupplierInvoice=[Updated Default Account for Supplier Invoice] from [OneLink_Master_New_FG_Load] f inner join [dbo].[GLString_CleanUP Work 20241004] c on ltrim(rtrim(f.[Default Account for Supplier Invoice]))=ltrim(rtrim(c.[Default Account for Supplier Invoice]))
        """,
        """
        -- (2083 rows affected) apply elly updates
update [dbo].[OneLink_Master_New_FG_Load] set cleansedDefaultAccountforSupplierInvoice=[Updated Default Account for Supplier Invoice] from [OneLink_Master_New_FG_Load] f inner join [dbo].[GLString_CleanUP Work 20241004] c on ltrim(rtrim(f.ellyGLString))=ltrim(rtrim(c.[Default Account for Supplier Invoice])) where ellyGLString is not null
        """,
        """
        -- (25 rows affected) for prod
update [dbo].[OneLink_Master_New_FG_Load] set updatedDefaultAccountforSupplierInvoice=g.[Name] from [dbo].[OneLink_Master_New_FG_Load] j inner join [dbo].[AccountMaster_PROD_20241018] g on ltrim(rtrim(j.cleansedDefaultAccountforSupplierInvoice))=ltrim(rtrim(g.[Code]))
        """,
        """
        -- (2054 rows affected) create csv for load for JO's (FG Enabled)
select [Contract Header] ,[Contract Name] ,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,replace([Parent Contract Number],'OL_','') as [Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://'+[Contract #]+'/'+[Contract #]+'_LA.zip' as [Legal Agreement] --[Legal Agreement] -- ,[Currency] ,[Source] ,[Supplier Account #] ,updatedOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'Kaiser Permanente Corporation'  as  [Default Account Type for Supplier Invoice]--'Kaiser Permanente Corporation' ,updatedDefaultAccountforSupplierInvoice as [Default Account for Supplier Invoice] -- updatedDefaultAccountforSupplierInvoice ,[Savings %] ,[Minimum Spend] ,replace([Maximum Spend],',','') as [Maximum Spend] ,[Stop Spend Over Contract Value] ,'Fieldglass' as [Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://'+[Contract #]+'/'+[Contract #]+'_ATT.zip' as [Attachment 1]--[Attachment 1] -- ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,'No' as [Used For Buying] -- all No for FG enabled suppliers ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,'JO - Job Order' as [Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,isnull([Price & Payment Contract Type Custom Field 1],'0') as [Price & Payment Contract Type Custom Field 1] ,isnull([Price & Payment Contract Type Custom Field 2],'0') as [Price & Payment Contract Type Custom Field 2] ,isnull([Price & Payment Contract Type Custom Field 3],'0') as [Price & Payment Contract Type Custom Field 3] ,isnull([Price & Payment Contract Type Custom Field 4],'0') as [Price & Payment Contract Type Custom Field 4] ,isnull([Price & Payment Contract Type Custom Field 5],'0') as [Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,isnull(updatedBusinessUser,'P529206') as [Business User*] , [Engagement Type] ,updatedEngagementManager as [Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,case when [Commodity Name] like '%Professional%' then 'Professional Services' else 'Consulting' end as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_load] where [Supplier Number]  in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers]) and [External Contract Identifier] in ('FG_0000000000000000019188') order by [External Contract Identifier]
        """,
        """
        -- Create CSV for Non FG Enabled JO Non-FG Enabled Suppliers
select [Contract Header] ,[Contract Name] ,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,replace([Parent Contract Number],'OL_','') as [Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,updatedOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'Kaiser Permanente Corporation'  as [Default Account Type for Supplier Invoice] ,updatedDefaultAccountforSupplierInvoice as [Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,replace([Maximum Spend],',','') as [Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,'JO - Job Order' as [Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,replace(isnull([Price & Payment Contract Type Custom Field 1],'0'),'','0') as [Price & Payment Contract Type Custom Field 1] ,replace(isnull([Price & Payment Contract Type Custom Field 2],'0'),'','0') as [Price & Payment Contract Type Custom Field 2] ,replace(isnull([Price & Payment Contract Type Custom Field 3],'0'),'','0') as [Price & Payment Contract Type Custom Field 3] ,replace(isnull([Price & Payment Contract Type Custom Field 4],'0'),'','0') as [Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,updatedBusinessUser as [Business User*] ,[Engagement Type] ,updatedEngagementManager as [Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,case when [Commodity Name] like '%Professional%' then 'Professional Services' else 'Consulting' end as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] from OneLink_Master_New_FG_Load where  [External Contract Identifier] in ('0000000000000000000020102') and [Supplier Number] not in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        select DISTINCT [Contract Type Name] from [dbo].[OneLink_Master_New_FG_Load]
        """,
        """
        select DISTINCT [Contract Type Name] from [dbo].[OneLink_Master_New_FG_Delta]
        """,
        """
        -- insert JO into Load table
insert into [OneLink_Master_New_FG_Load] Select *, null,'Non-FG',null,null,null,null,null,null,null,null from OneLink_Master_New_FG where [Contract Type Name] ='LOA - Letter of Agreement'
        """,
        """
        -- 54 work out deltas delta processing (remove old contract and load delta)
Select * from [dbo].[OneLink_Master_New_FG_Delta] where [Contract Type Name] ='LOA - Letter of Agreement'
        """,
        """
        -- 14 delete from orig if exists in delta
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta]) and [Contract Type Name] ='LOA - Letter of Agreement'
        """,
        """
        -- (2 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select *, null,'Non-FG',null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='LOA - Letter of Agreement'
        """,
        """
        -- (14 rows affected) 10/14 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241014]) and [Contract Type Name]='LOA - Letter of Agreement'
        """,
        """
        -- (0 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select *,null,'Non-FG',null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241014] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='LOA - Letter of Agreement'
        """,
        """
        -- (3 rows affected) 10/18 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241018]) and [Contract Type Name]='LOA - Letter of Agreement'
        """,
        """
        -- (0 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select * ,null,'Non-FG',null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241018] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='LOA - Letter of Agreement'
        """,
        """
        -- (0 rows affected) update FG flag for FG suppliers
update [OneLink_Master_New_FG_Load] set FG='FG' where ltrim(rtrim([Supplier Number])) in (Select ltrim(rtrim([VENDOR_ID])) from FG_EnabledSuppliers) and [Contract Type Name]='LOA - Letter of Agreement'
        """,
        """
        -- (35 rows affected)
select distinct FG from [OneLink_Master_New_FG_Load]
        """,
        """
        select distinct [External Contract Identifier],[Contract #] from [OneLink_Master_New_FG_Load] where [Contract Type Name] like '%LOA%' and FG='Non-FG'
        """,
        """
        -- Only 34 prep load contract file csv with active status for loading JO only (R file) -- AmtLineMax
drop table [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_LOA select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_LOA from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX]
        """,
        """
        -- from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d
from  [dbo].[FG Consumption data Oct26_filtered])d--from [dbo].[FG_LOA-SOW-1018])d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee],[sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        -- (877 rows affected) JO Only -- Consumed Amt
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_LOA select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_LOA from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_RELEASED]
        """,
        """
        -- from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d
from  [dbo].[FG Consumption data Oct26_filtered])d --from [dbo].[FG_LOA-SOW-1018])d pivot ( max([AMT_LINE_RELEASED]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses, [Program Fee])
        """,
        """
        ) piv;
        """,
        """
        -- (877 rows affected)
alter table [OneLink_Master_New_FG_Load] add [sPro/Legacy Consumed (paid)] nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_expenses nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_programfee nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_TimeandMaterial_managedTeams nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_fixedfeeManagedService nvarchar(255)
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Fixed Fee/Manage Service] ,[Price & Payment Contract Type Custom Field 2]=a.[Time & Material / Managed Teams] ,[Price & Payment Contract Type Custom Field 3]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] ,[Price & Payment Contract Type Custom Field 5]=a.[Program Fee] ,[sPro/Legacy Consumed (paid)] = a.[sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_LOA] a on l.[External Contract Identifier]=a.[CNTRCT_ID] where l.[Contract Type Name] ='LOA - Letter of Agreement';
        """,
        """
        -- (35 rows affected)
update [OneLink_Master_New_FG_Load] set consumed_fixedfeeManagedService=a.[Fixed Fee/Manage Service] ,consumed_TimeandMaterial_managedTeams=a.[Time & Material / Managed Teams] ,consumed_expenses=a.[Expenses] ,consumed_programfee=a.[Program Fee] from [OneLink_Master_New_FG_Load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_LOA a on l.[External Contract Identifier]=a.[CNTRCT_ID] where l.[Contract Type Name] ='LOA - Letter of Agreement'
        """,
        """
        -- (35 rows affected)
update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]='0' where [Price & Payment Contract Type Custom Field 1]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 2]='0' where [Price & Payment Contract Type Custom Field 2]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 3]='0' where [Price & Payment Contract Type Custom Field 3]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 4]='0' where [Price & Payment Contract Type Custom Field 4]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 5]='0' where [Price & Payment Contract Type Custom Field 5]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]='0' where [Price & Payment Contract Type Custom Field 1] is null;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 2]='0' where [Price & Payment Contract Type Custom Field 2] is null;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 3]='0' where [Price & Payment Contract Type Custom Field 3] is null;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 4]='0' where [Price & Payment Contract Type Custom Field 4] is null;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 5]='0' where [Price & Payment Contract Type Custom Field 5] is null;
        """,
        """
        select distinct [Price & Payment Contract Type Custom Field 1] from [OneLink_Master_New_FG_Load]
        """,
        """
        -- gl string
select distinct [Default Account for Supplier Invoice] from  [dbo].[OneLink_Master_New_FG_Load] where [Supplier Number]  in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers]) and updated_contract_# in  ('FG_0000000000000000019159','FG_0000000000000000019161')
        """,
        """
        alter table [dbo].[OneLink_Master_New_FG_Load] add updatedDefaultAccountforSupplierInvoice nvarchar(500)
        """,
        """
        -- make sure load table has cleansed [Default Account for Supplier Invoice] so we can join to accounts table properly
update [dbo].[OneLink_Master_New_FG_Load] set cleansedDefaultAccountforSupplierInvoice=[Updated Default Account for Supplier Invoice] from [OneLink_Master_New_FG_Load] f inner join [dbo].[GLString_CleanUP Work 20241004] c on ltrim(rtrim(f.[Default Account for Supplier Invoice]))=ltrim(rtrim(c.[Default Account for Supplier Invoice]))
        """,
        """
        -- (2081 rows affected) for prod
update [dbo].[OneLink_Master_New_FG_Load] set updatedDefaultAccountforSupplierInvoice=g.[Name] from [dbo].[OneLink_Master_New_FG_Load] j inner join [dbo].[AccountMaster_PROD_20241018] g on ltrim(rtrim(j.cleansedDefaultAccountforSupplierInvoice))=ltrim(rtrim(g.[Code]))
        """,
        """
        -- (1993 rows affected) create csv for load for LOA's (FG Enabled)
select [Contract Header] ,[Contract Name] ,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,'' as [Parent Contract Number] ,'' as [Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://'+[Contract #]+'/'+[Contract #]+'_LA.zip' as [Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,updatedOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'Kaiser Permanente Corporation'  as  [Default Account Type for Supplier Invoice]--'Kaiser Permanente Corporation' ,updatedDefaultAccountforSupplierInvoice as [Default Account for Supplier Invoice] -- updatedDefaultAccountforSupplierInvoice ,[Savings %] ,[Minimum Spend] ,replace([Maximum Spend],',','') as [Maximum Spend] ,[Stop Spend Over Contract Value] ,'Fieldglass' as [Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://'+[Contract #]+'/'+[Contract #]+'_ATT.zip' as [Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,'No' as [Used For Buying] -- all No for FG enabled suppliers ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,isnull([Price & Payment Contract Type Custom Field 1],'0') as [Price & Payment Contract Type Custom Field 1] ,isnull([Price & Payment Contract Type Custom Field 2],'0') as [Price & Payment Contract Type Custom Field 2] ,isnull([Price & Payment Contract Type Custom Field 3],'0') as [Price & Payment Contract Type Custom Field 3] ,isnull([Price & Payment Contract Type Custom Field 4],'0') as [Price & Payment Contract Type Custom Field 4] ,isnull([Price & Payment Contract Type Custom Field 5],'0') as [Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,updatedBusinessUser as [Business User*] , [Engagement Type] ,updatedEngagementManager as[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,case when [Commodity Name] like '%Professional%' then 'Professional Services' else 'Consulting' end as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_load] where [Supplier Number]  in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers]) and [External Contract Identifier] in ('0000000000000000000016190','0000000000000000000016842','0000000000000000000017711','0000000000000000000019012','0000000000000000000019894') order by [External Contract Identifier]
        """,
        """
        -- Create CSV for Non FG Enabled LOA's Non-FG Enabled Suppliers
select [Contract Header] ,[Contract Name] ,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,'' as [Parent Contract Number] ,'' as [Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://'+[Contract #]+'/'+[Contract #]+'_LA.zip' as [Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,updatedOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'Kaiser Permanente Corporation'  as  [Default Account Type for Supplier Invoice]--'Kaiser Permanente Corporation' ,updatedDefaultAccountforSupplierInvoice as [Default Account for Supplier Invoice] -- updatedDefaultAccountforSupplierInvoice ,[Savings %] ,[Minimum Spend] ,replace([Maximum Spend],',','') as [Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://'+[Contract #]+'/'+[Contract #]+'_ATT.zip' as [Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,replace(isnull([Price & Payment Contract Type Custom Field 1],'0'),'','0') as [Price & Payment Contract Type Custom Field 1] ,replace(isnull([Price & Payment Contract Type Custom Field 2],'0'),'','0') as [Price & Payment Contract Type Custom Field 2] ,replace(isnull([Price & Payment Contract Type Custom Field 3],'0'),'','0') as [Price & Payment Contract Type Custom Field 3] ,replace(isnull([Price & Payment Contract Type Custom Field 4],'0'),'','0') as [Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,updatedBusinessUser as [Business User*] ,[Engagement Type] ,updatedEngagementManager as [Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,case when [Commodity Name] like '%Professional%' then 'Professional Services' else 'Consulting' end as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] from OneLink_Master_New_FG_Load where  [External Contract Identifier] in ('0000000000000000000018862','0000000000000000000021180','0000000000000000000021184') and [Supplier Number] not in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        Select distinct filename from OneLink_Master_New_FG
        """,
        """
        -- FG LOA
Select * from OneLink_Master_New_FG where filename ='G_2024-05-30'
        """,
        """
        -- 54 these LOA's are closed contracts who has an active counterpart.. move this to python script so it can move documents try new version. first get all contracts that have 2 versions G -- find contracts whose FG version only was sent
select distinct SUBSTRING(replace(replace([Contract #],'FG_',''),'OL_',''), PATINDEX('%[^0]%', replace(replace([Contract #],'FG_',''),'OL_','')) , LEN(replace(replace([Contract #],'FG_',''),'OL_',''))) as Matched_Contract_# ,[Contract #], updated_contract_#, updated_contract_status, Expires into [dbo].[OneLink_Master_New_FG_ContractNumbers_LOA] from [dbo].[OneLink_Master_New_FG] where filename ='G_2024-05-30' and ltrim(rtrim([Supplier Number])) In (Select distinct ltrim(rtrim([Vendor id])) from FG_EnabledSuppliers) and cast(expires as date)>'2024-01-31'
        """,
        """
        Select * from [OneLink_Master_New_FG_ContractNumbers_R] where Matched_Contract_# in (select Matched_Contract_# from [dbo].[OneLink_Master_New_FG_ContractNumbers_R] group by Matched_Contract_# having count(*)>1)
        """,
        """
        -- create a table with master contract number,new contract number and old contract number
select matched_contract_#, isnull(updated_contract_#,replace([Contract #],'OL_','')) as New_Contract_Number into [dbo].[OneLink_Master_New_FG_ContractNumberMaster_R] from [dbo].[OneLink_Master_New_FG_ContractNumbers_R] where updated_contract_# like 'FG%'
        """,
        """
        update [OneLink_Master_New_FG_ContractNumberMaster_R] set Old_Contract_Number=isnull(updated_contract_#,replace([Contract #],'OL_','')) from [OneLink_Master_New_FG_ContractNumberMaster_R] a inner join [OneLink_Master_New_FG_ContractNumbers_R] b on a.matched_contract_#=b.matched_contract_# where updated_contract_# not like 'FG%'
        """,
        """
        select * from [OneLink_Master_New_FG_ContractNumberMaster_R] where old_contract_number is null order by matched_contract_#
        """,
        """
        -- prep load contract file csv with active status for loading JO only (R file) -- AmtLineMax
drop table [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX] from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee],[sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        -- (1009 rows affected) JO Only -- Consumed Amt
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_RELEASED] from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d pivot ( max([AMT_LINE_RELEASED]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses, [Program Fee])
        """,
        """
        ) piv;
        """,
        """
        -- 1009 *********** pending check how to populate final released amount field ********* update load table with additional custom fields so we can export load file 1. pick JO as first pass with complex logic
select * from [OneLink_Master_New_FG_R_Load] a where updated_contract_# in ('FG_0000000000000000004600','FG_0000000000000000006266','FG_0000000000000000007439','FG_0000000000000000015410' ,'FG_0000000000000000015593','FG_0000000000000000016815','FG_0000000000000000018687','FG_0000000000000000018711','FG_0000000000000000018782' ,'FG_0000000000000000018815','FG_0000000000000000019188','FG_0000000000000000019646','FG_0000000000000000020289')
        """,
        """
        -- run update on custom fields
select distinct [Price & Payment Contract Type Custom Field 1],[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3],[Price & Payment Contract Type Custom Field 4],[Price & Payment Contract Type Custom Field 5] from [OneLink_Master_New_FG_R_Load]
        """,
        """
        alter table [OneLink_Master_New_FG_R_Load] add [sPro/Legacy Consumed (paid)] nvarchar(255)
        """,
        """
        update [OneLink_Master_New_FG_R_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Fixed Fee/Manage Service] ,[Price & Payment Contract Type Custom Field 2]=a.[Time & Material / Managed Teams] ,[Price & Payment Contract Type Custom Field 3]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] ,[Price & Payment Contract Type Custom Field 5]=a.[Program Fee] ,[sPro/Legacy Consumed (paid)] = a.[sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_R_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB] a on l.[updated_contract_#]=a.[CNTRCT_ID] where l.[updated_contract_#] in ('FG_0000000000000000004600','FG_0000000000000000006266','FG_0000000000000000007439','FG_0000000000000000015410' ,'FG_0000000000000000015593','FG_0000000000000000016815','FG_0000000000000000018687','FG_0000000000000000018711','FG_0000000000000000018782' ,'FG_0000000000000000018815','FG_0000000000000000019188','FG_0000000000000000019646','FG_0000000000000000020289')
        """,
        """
        alter table [OneLink_Master_New_FG_R_Load] add [sPro/Legacy Consumed (paid)] nvarchar(255)
        """,
        """
        alter table [OneLink_Master_New_FG_R_Load] add expenses nvarchar(255)
        """,
        """
        alter table [OneLink_Master_New_FG_R_Load] add consumed_programfee nvarchar(255)
        """,
        """
        alter table [OneLink_Master_New_FG_R_Load] add consumed_TimeandMaterial_managedTeams nvarchar(255)
        """,
        """
        alter table [OneLink_Master_New_FG_R_Load] add consumed_fixedfeeManagedService nvarchar(255)
        """,
        """
        update [OneLink_Master_New_FG_R_Load] set consumed_fixedfeeManagedService=a.[Fixed Fee/Manage Service] ,consumed_TimeandMaterial_managedTeams=a.[Time & Material / Managed Teams] ,expenses=a.[Expenses] ,consumed_programfee=a.[Program Fee] from [OneLink_Master_New_FG_R_Load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Consumed_JOB a on l.[updated_contract_#]=a.[CNTRCT_ID] where l.[updated_contract_#] in ('FG_0000000000000000004600','FG_0000000000000000006266','FG_0000000000000000007439','FG_0000000000000000015410' ,'FG_0000000000000000015593','FG_0000000000000000016815','FG_0000000000000000018687','FG_0000000000000000018711','FG_0000000000000000018782' ,'FG_0000000000000000018815','FG_0000000000000000019188','FG_0000000000000000019646','FG_0000000000000000020289')
        """,
        """
        -- looks for old counterparts
Select * from [OneLink_Master_New_FG_ContractNumberMaster_R] where  New_Contract_Number in ('FG_0000000000000000004600','FG_0000000000000000006266','FG_0000000000000000007439','FG_0000000000000000015410' ,'FG_0000000000000000015593','FG_0000000000000000016815','FG_0000000000000000018687','FG_0000000000000000018711','FG_0000000000000000018782' ,'FG_0000000000000000018815','FG_0000000000000000019188','FG_0000000000000000019646','FG_0000000000000000020289')
        """,
        """
        -- now build export csv create csv for load for MSOW's
select [Contract Header] ,[Contract Name] ,replace([Contract #],'OL_','') as [Contract #] -- this is for FG enabled supplier only ,case when [Contract Type Name]='MSOW - Master Statement of Work' then 'Master' else 'Contract' end as [Hierarchy Type] ,'' as [Parent Contract Number] ,'' as [Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://OL_'+updated_contract_#+'/OL_'+updated_contract_#+'_LA.zip' as [Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,'G294578' as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,[Default Account for Supplier Invoice Updated] as [Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] -- all No for FG enabled suppliers ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://OL_'+updated_contract_#+'/OL_'+updated_contract_#+'_ATT.zip' as [Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,'No' as [Used For Buying] -- all No for FG enabled suppliers ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,case when [Contract Type Name]='JOB' then 'JO - Job Order' else [Contract Type Name] end ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Parent Contract Number] as [Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,isnull([Price & Payment Contract Type Custom Field 1],'') as [Price & Payment Contract Type Custom Field 1] ,isnull([Price & Payment Contract Type Custom Field 2],'') as [Price & Payment Contract Type Custom Field 2] ,isnull([Price & Payment Contract Type Custom Field 3],'') as [Price & Payment Contract Type Custom Field 3] ,isnull([Price & Payment Contract Type Custom Field 4],'') as [Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,'G294578' as [Business User*] , [Engagement Type] ,'G294578' as[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,'Consulting' as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +'|| Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +'|| T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +'|| Expenses Consumed Amount ='+FORMAT(cast(isnull([expenses],'') as float),'C') +'|| Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_R_Load] where [Supplier Number]  in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers]) and updated_contract_# in
        """,
        """
        -- validate all contracts have been considered
select distinct [Contract #],[External Contract Identifier] from [dbo].[OneLink_Master_New_FG] where [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        select *
        """,
        """
        -- into [dbo].[OneLink_Master_New_FG_Load]
from [dbo].[OneLink_Master_New_FG_load] where [Contract Type Name]='MSOW - Master Statement of Work' and [External Contract Identifier] like '%8629%'
        """,
        """
        -- (113 rows affected) remove unnecessary fields
alter table OneLink_Master_New_FG_Load drop column [updated_contract_#]; alter table OneLink_Master_New_FG_Load drop column [updated_parent_contract_#] ; alter table OneLink_Master_New_FG_Load drop column [updated_contract_status];
        """,
        """
        -- delta processing (remove old contract and load delta)
Select * from [dbo].[OneLink_Master_New_FG_Delta] where [Contract Type Name]='MSOW - Master Statement of Work' and [External Contract Identifier] like '%21278%'
        """,
        """
        -- delete from orig if exists in delta
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta]) and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- (12 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select * from [dbo].[OneLink_Master_New_FG_Delta] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- (12 rows affected) 10/14 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241014]) and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- (5 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select *,'B_2024-10-14.csv',null,'Non-FG',null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241014] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- (5 rows affected) 10/18 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241018]) and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- (2 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select * ,'B_2024-10-18.csv',null,'Non-FG',null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241018] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- (2 rows affected) 10/25 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241025]) and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- (3 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select * ,null,'Non-FG',null,null,null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241025] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- (3 rows affected) adhoc load (I know this contract is not in load table)
insert into [dbo].[OneLink_Master_New_FG_Load] select * ,null,'Non-FG',null,null,null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG] d where [Contract #]='OL_CID_1770-3911-16952' and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- (1 row affected)
select * from [dbo].[OneLink_Master_New_FG_Load]
        """,
        """
        -- Consumption work prep load contract file csv with active status for loading MSOW only (B file) -- AmtLineMax
drop table [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX]
        """,
        """
        -- from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d
from  [dbo].[FG Consumption data Oct26_filtered])d --from [dbo].[FG_MSOW-JO-1018])d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Hybrid/Uncategorized],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee]) ) piv;
        """,
        """
        -- (877 rows affected) MSOW Only -- Consumed Amt ([sPro/Legacy Consumed (paid)])
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW_SPro select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW_SPro from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX]
        """,
        """
        -- from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d
from  [dbo].[FG Consumption data Oct26_filtered])d --from [dbo].[FG_MSOW-JO-1018])d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        -- (877 rows affected) update load table with additional custom fields so we can export load file run update on custom fields
select distinct [Price & Payment Contract Type Custom Field 1],[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3],[Price & Payment Contract Type Custom Field 4],[Price & Payment Contract Type Custom Field 5] from [OneLink_Master_New_FG_Load]
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Hybrid/Uncategorized] ,[Price & Payment Contract Type Custom Field 2]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 3]=a.[Program Fee] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] from [OneLink_Master_New_FG_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW] a on l.[External Contract Identifier]=a.[CNTRCT_ID] where [Supplier Number] in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers]) and [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- 0
update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]='0' where [Price & Payment Contract Type Custom Field 1]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 2]='0' where [Price & Payment Contract Type Custom Field 2]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 3]='0' where [Price & Payment Contract Type Custom Field 3]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 4]='0' where [Price & Payment Contract Type Custom Field 4]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 5]='0' where [Price & Payment Contract Type Custom Field 5]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]='0' where [Price & Payment Contract Type Custom Field 1] is null;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 2]='0' where [Price & Payment Contract Type Custom Field 2] is null;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 3]='0' where [Price & Payment Contract Type Custom Field 3] is null;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 4]='0' where [Price & Payment Contract Type Custom Field 4] is null;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 5]='0' where [Price & Payment Contract Type Custom Field 5] is null;
        """,
        """
        -- consumed amount??
update [OneLink_Master_New_FG_Load] set [Price & Payment sPro Pre-Consumed/FG Consumed amount] = a.[sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_Load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW_SPro a on l.[External Contract Identifier]=a.[CNTRCT_ID] where  [Supplier Number] in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers]) and  [Contract Type Name]='MSOW - Master Statement of Work'
        """,
        """
        -- 0 updating to angel when blank
update [dbo].OneLink_Master_New_FG_LOAD set updatedBusinessUser=[Business User*];
        """,
        """
        -- 2083 update to Angel
update [dbo].OneLink_Master_New_FG_LOAD set updatedBusinessUser='P529206' from [dbo].OneLink_Master_New_FG_LOAD e where not exists (Select 'x' from [dbo].[coupa_users] u where e.[Business User*]=u.Login and u.Active='Active');
        """,
        """
        -- (71 rows affected) [Engagement Manager]
update [dbo].OneLink_Master_New_FG_LOAD set updatedEngagementManager=[Engagement Manager];
        """,
        """
        -- (2083 rows affected)
update [dbo].OneLink_Master_New_FG_LOAD set updatedEngagementManager='' from [dbo].OneLink_Master_New_FG_LOAD e where  not exists (Select 'x' from [dbo].[coupa_users] u where e.[Engagement Manager]=u.Login and u.Active='Active');
        """,
        """
        -- (249 rows affected) update owner logins with replacement
update OneLink_Master_New_FG_LOAD set updatedOwnerLogin=[Owner Login]
        """,
        """
        -- 2091
update OneLink_Master_New_FG_LOAD set updatedOwnerLogin=[Replacement ID] from OneLink_Master_New_FG_LOAD f inner join replacementUsers u on ltrim(rtrim(f.[Owner Login]))=ltrim(rtrim(u.[Old Owner Login]))
        """,
        """
        -- (355 rows affected) now build export csv for Hierarchy =Master , GL Account is  set it all to blank for now create csv for load for MSOW's FG enabled supplier only
select [Contract Header] ,[Contract Name]
        """,
        """
        -- ,replace([Contract #],'OL_','') as [Contract #] -- this is for FG enabled supplier only
,[External Contract Identifier] as [Contract #] ,'Master'  as [Hierarchy Type] ,'' as [Parent Contract Number] ,'' as [Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://'+[Contract #]+'/'+[Contract #]+'_LA.zip' as [Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,updatedOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'' as [Default Account Type for Supplier Invoice] ,'' as [Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,replace([Maximum Spend],',','') as [Maximum Spend] ,[Stop Spend Over Contract Value] ,'Fieldglass' as [Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://'+[Contract #]+'/'+[Contract #]+'_ATT.zip' as [Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,'No' as [Used For Buying] -- all No for FG enabled suppliers ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,case when left([Default Account for Supplier Invoice],4)='9601' then 'IT - MSOW: '+[Description] else 'Non-IT - MSOW: '+[Description] end as [Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,replace(isnull([Contract Type Custom Field 1],'0'),'','0') as [Contract Type Custom Field 1] ,replace(isnull([Contract Type Custom Field 2],'0'),'','0') as [Contract Type Custom Field 2] ,replace(isnull([Contract Type Custom Field 3],'0'),'','0') as [Contract Type Custom Field 3] ,replace(isnull([Contract Type Custom Field 4],'0'),'','0') as [Contract Type Custom Field 4] ,replace(isnull([Contract Type Custom Field 5],'0'),'','0') as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Parent Contract Number] as [Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,replace(isnull([Price & Payment Contract Type Custom Field 1],'0'),'','0') as [Price & Payment Contract Type Custom Field 1] ,replace(isnull([Price & Payment Contract Type Custom Field 2],'0'),'','0') as [Price & Payment Contract Type Custom Field 2] ,replace(isnull([Price & Payment Contract Type Custom Field 3],'0'),'','0') as [Price & Payment Contract Type Custom Field 3] ,replace(isnull([Price & Payment Contract Type Custom Field 4],'0'),'','0') as [Price & Payment Contract Type Custom Field 4] ,replace(isnull([Price & Payment Contract Type Custom Field 5],'0'),'','0') as [Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,updatedBusinessUser as [Business User*] ,[Engagement Type] ,updatedEngagementManager as [Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,'Consulting' as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([Price & Payment sPro Pre-Consumed/FG Consumed amount],'') as float),'C')+'"' as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_Load] where  [External Contract Identifier] in ('FG_0000000000000000010989','FG_184-3576-17058') and [Supplier Number]  in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- Non-FG Enabled Suppliers
select [Contract Header] ,[Contract Name] ,[External Contract Identifier] as [Contract #] ,'Master' as [Hierarchy Type] ,'' as [Parent Contract Number] ,'' as [Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://'+[Contract #]+'/'+[Contract #]+'_LA.zip' as [Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,updatedOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,'' as [Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,replace([Maximum Spend],',','') as [Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://'+[Contract #]+'/'+[Contract #]+'_ATT.zip' as [Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,replace(isnull([Contract Type Custom Field 1],0),'',0) as [Contract Type Custom Field 1] ,replace(isnull([Contract Type Custom Field 2],0),'',0) as [Contract Type Custom Field 2] ,replace(isnull([Contract Type Custom Field 3],0),'',0) as [Contract Type Custom Field 3] ,replace(isnull([Contract Type Custom Field 4],0),'',0) as [Contract Type Custom Field 4] ,replace(isnull([Contract Type Custom Field 5],0),'',0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Parent Contract Number] as [Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,replace(isnull([Price & Payment Contract Type Custom Field 1],'0'),'','0') as [Price & Payment Contract Type Custom Field 1] ,replace(isnull([Price & Payment Contract Type Custom Field 2],'0'),'','0') as [Price & Payment Contract Type Custom Field 2] ,replace(isnull([Price & Payment Contract Type Custom Field 3],'0'),'','0') as [Price & Payment Contract Type Custom Field 3] ,replace(isnull([Price & Payment Contract Type Custom Field 4],'0'),'','0') as [Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,updatedBusinessUser as [Business User*] ,[Engagement Type] ,updatedEngagementManager as [Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,'Consulting' as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] from OneLink_Master_New_FG_Load where  [External Contract Identifier] in ('0000000000000000000010940','0000000000000000000014197','0000000000000000000017702') and [Supplier Number] not in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        update [OneLink_Master_New_FG] set filename ='R_2024-05-30' where filename is null delete from [OneLink_Master_New_FG] where [Contract Header] IN ('Contract Party','Contract Party Contact')
        """,
        """
        select * from [dbo].[OneLink_Master_New_FG] -- where [Contract #] like '%12968' select * from FG_AdditionalInformation --where [CNTRCT_ID] like '%12968'
        """,
        """
        select * from [FG_JO_MSOW]
        """,
        """
        alter table [OneLink_Master_New_FG] add  updated_contract_# nvarchar(255)
        """,
        """
        alter table [OneLink_Master_New_FG] add  updated_parent_contract_# nvarchar(255)
        """,
        """
        alter table [OneLink_Master_New_FG] add  updated_contract_status nvarchar(255)
        """,
        """
        -- update FG table from file Meena sent for contract #, parent contract #
update [OneLink_Master_New_FG] set updated_contract_#= m.[CNTRCT_ID], updated_parent_contract_#= m.[PARENT_CONTR_ID],updated_contract_status=m.[CNTRCT_STATUS] from [OneLink_Master_New_FG] o inner join [dbo].[FG_JO_MSOW] m on o.[External Contract Identifier]=m.[CNTRCT_ID]
        """,
        """
        -- 659 create FG Enabled Supplier Only Table
insert into  FG_AdditionalInformation_FGEnabledSuppliers select * from FG_AdditionalInformation where [VENDOR_ID] in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- MSOW Only table (B file)
drop table [OneLink_Master_New_FG_B_Load] select * into [dbo].[OneLink_Master_New_FG_B_Load] from [dbo].[OneLink_Master_New_FG] where filename='B_2024-05-30' and updated_contract_status='A'
        """,
        """
        -- 63 out of 113
drop table [OneLink_Master_New_FG_R_Load] select * into [dbo].[OneLink_Master_New_FG_R_Load] from [dbo].[OneLink_Master_New_FG] where  filename='R_2024-05-30' and updated_contract_status='A'
        """,
        """
        -- 328 out of 562 idenfity the closed contracts who have an active counterpart in load table to move LA and attachments over MSOW
select distinct [updated_contract_#],SUBSTRING(replace([updated_contract_#],'FG_',''), PATINDEX('%[^0]%', replace([updated_contract_#],'FG_','')), LEN(replace([updated_contract_#],'FG_',''))),updated_contract_status from [OneLink_Master_New_FG] order by 2
        """,
        """
        -- handle these separately
select * from [OneLink_Master_New_FG] where [updated_contract_#] is null
        """,
        """
        -- 16 these MSOW's are closed contracts who has an active counterpart.. move this to python script so it can move documents do not use this but the script below
select distinct [updated_contract_#] from [dbo].[OneLink_Master_New_FG] c where  exists (Select 'X' from [dbo].[OneLink_Master_New_FG] a where SUBSTRING(replace(c.[updated_contract_#],'FG_',''), PATINDEX('%[^0]%', replace(c.[updated_contract_#],'FG_','')), LEN(replace(c.[updated_contract_#],'FG_',''))) =SUBSTRING(replace(a.[updated_contract_#],'FG_',''), PATINDEX('%[^0]%', replace(a.[updated_contract_#],'FG_','')), LEN(replace(a.[updated_contract_#],'FG_',''))) and a.updated_contract_status='A' and filename='B_2024-05-30') and filename='B_2024-05-30' and updated_contract_status='C'
        """,
        """
        -- create a table with master contract number,new contract number and old contract number
select matched_contract_#, isnull(updated_contract_#,replace([Contract #],'OL_','')) as New_Contract_Number into [dbo].[OneLink_Master_New_FG_ContractNumberMaster_B] from [dbo].[OneLink_Master_New_FG_ContractNumbers_B] where updated_contract_# like 'FG%'
        """,
        """
        -- 44
alter table [OneLink_Master_New_FG_ContractNumberMaster_B] add Old_Contract_Number nvarchar(255)
        """,
        """
        update [OneLink_Master_New_FG_ContractNumberMaster_B] set Old_Contract_Number=isnull(updated_contract_#,replace([Contract #],'OL_','')) from [OneLink_Master_New_FG_ContractNumberMaster_B] a inner join [OneLink_Master_New_FG_ContractNumbers_B] b on a.matched_contract_#=b.matched_contract_# where updated_contract_# not like 'FG%'
        """,
        """
        -- 36
select * from [OneLink_Master_New_FG_ContractNumberMaster_B]
        """,
        """
        -- where old_contract_number is null
order by matched_contract_#
        """,
        """
        -- prep load contract file csv with active status for loading MSOW only (B file) -- AmtLineMax
drop table [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX] from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Hybrid/Uncategorized],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee]) ) piv;
        """,
        """
        -- (1009 rows affected) MSOW Only -- Consumed Amt ([sPro/Legacy Consumed (paid)])
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW_SPro select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW_SPro from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX] from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        -- 1009 update load table with additional custom fields so we can export load file 1. pick few MSOW's as first pass with complex logic
select * from [OneLink_Master_New_FG_B_Load] a where SUBSTRING(replace(a.[updated_contract_#],'FG_',''), PATINDEX('%[^0]%', replace(a.[updated_contract_#],'FG_','')), LEN(replace(a.[updated_contract_#],'FG_',''))) in ('3248','3477','3478')
        """,
        """
        -- check vendor id in FG enabled list
select * from [OneLink_Master_New_FG_B_Load] where SUBSTRING(replace([updated_contract_#],'FG_',''), PATINDEX('%[^0]%', replace([updated_contract_#],'FG_','')), LEN(replace([updated_contract_#],'FG_',''))) in ('3248','3477','3478')  and [Supplier Number] in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- perfect!!!!! all 3 are FG enabled.. what a pick MJ!! run update on custom fields
select distinct [Price & Payment Contract Type Custom Field 1],[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3],[Price & Payment Contract Type Custom Field 4],[Price & Payment Contract Type Custom Field 5] from [OneLink_Master_New_FG_B_Load]
        """,
        """
        update [OneLink_Master_New_FG_B_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Hybrid/Uncategorized] ,[Price & Payment Contract Type Custom Field 2]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 3]=a.[Program Fee] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] from [OneLink_Master_New_FG_B_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW] a on l.[updated_contract_#]=a.[CNTRCT_ID] where [Supplier Number] in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- 46
alter table [OneLink_Master_New_FG_B_Load] add [Price & Payment sPro Pre-Consumed/FG Consumed amount] nvarchar(255)
        """,
        """
        -- consumed amount??
update [OneLink_Master_New_FG_B_Load] set [Price & Payment sPro Pre-Consumed/FG Consumed amount] = [sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_B_Load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW_SPro a on l.[updated_contract_#]=a.[CNTRCT_ID] where  [Supplier Number] in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- 46 now build export csv for Hierarchy =Master , GL Account is not needed, set it all to blank create csv for load for MSOW's FG enabled supplier only
select [Contract Header] ,[Contract Name]
        """,
        """
        -- ,replace([Contract #],'OL_','') as [Contract #] -- this is for FG enabled supplier only
,[External Contract Identifier] as [Contract #] ,case when [Contract Type Name]='MSOW - Master Statement of Work' then 'Master' else 'Contract' end as [Hierarchy Type] ,'' as [Parent Contract Number] ,'' as [Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://OL_'+updated_contract_#+'/OL_'+updated_contract_#+'_LA.zip' as [Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,'G294578' as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'' as [Default Account Type for Supplier Invoice] ,'' as [Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://OL_'+updated_contract_#+'/OL_'+updated_contract_#+'_ATT.zip' as [Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,'No' as [Used For Buying] -- all No for FG enabled suppliers ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,case when left([Default Account for Supplier Invoice],4)='9601' then 'IT - MSOW: '+[Description] else 'Non-IT - MSOW:'+[Description] end as [Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Parent Contract Number] as [Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,isnull([Price & Payment Contract Type Custom Field 1],'') as [Price & Payment Contract Type Custom Field 1] ,isnull([Price & Payment Contract Type Custom Field 2],'') as [Price & Payment Contract Type Custom Field 2] ,isnull([Price & Payment Contract Type Custom Field 3],'') as [Price & Payment Contract Type Custom Field 3] ,isnull([Price & Payment Contract Type Custom Field 4],'') as [Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,'G294578' as [Business User*] , [Engagement Type] ,'G294578' as[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,'Consulting' as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([Price & Payment sPro Pre-Consumed/FG Consumed amount],'') as float),'C')+'"' as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_B_Load] where  [External Contract Identifier] in ('0000000000000000000021063','FG_0000000000000000020406')
        """,
        """
        -- ('0000000000000000000021063')--,'FG_0000000000000000020406') ('FG_0000000000000000013341','FG_0000000000000000013367','FG_0000000000000000013368','FG_0000000000000000013369','FG_0000000000000000013371','FG_0000000000000000013372','FG_0000000000000000013373','FG_0000000000000000013374','FG_0000000000000000013376','FG_0000000000000000013386','FG_0000000000000000013387') SUBSTRING(replace([updated_contract_#],'FG_',''), PATINDEX('%[^0]%', replace([updated_contract_#],'FG_','')), LEN(replace([updated_contract_#],'FG_',''))) in ('3248','3477','3478')
and [Supplier Number] in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        select * from [OneLink_Master_New_FG_B_Loaded]
        """,
        """
        insert into [dbo].[OneLink_Master_New_FG_B_Loaded] select
        """,
        """
        -- non-FG enabled supplier only
select distinct [Default Account for Supplier Invoice],left([Default Account for Supplier Invoice],4) from [dbo].[OneLink_Master_New_FG_B_Load] where [Contract #] like '%11460%' where  [Supplier Number] not in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- Parent contract number for MSOW will be blank, for JO parent contract should be mapped to the correct MSOW parent Meena's Request
select * from  [dbo].[OneLink_Master_New_FG_B_Load] where [Contract #] like '%21063%' 0000000000000000000021201 -- not there FG_21178 -- SOW 0000000000000000000021183 -- not there 0000000000000000000021132 -- JO 0000000000000000000021135 -- SOW 0000000000000000000021063 -- MSOW FG_0000000000000000020406 -- MSOW 0000000000000000000021166 -- not there 0000000000000000000021188 -- not there FG_0000000000000000019646 -- JO FG_0000000000000000018815 -- JO
        """,
        """
        select * from  [dbo].[OneLink_Master_New_FG_R_Load] where [Contract #] like '%21188%'
        """,
        """
        select distinct *
        """,
        """
        -- [Contract #],[Contract Type Name]
from  [dbo].[OneLink_Master_New_FG] where [Contract #] like '%21063%'
        """,
        """
        select DISTINCT [Contract Type Name] from [dbo].[OneLink_Master_New_FG_Load]
        """,
        """
        select DISTINCT [Contract Type Name] from [dbo].[OneLink_Master_New_FG_Delta]
        """,
        """
        -- insert SOW's into Load table insert into [OneLink_Master_New_FG_Load]
Select *, null,'Non-FG',null,null,null,null,null,null from OneLink_Master_New_FG where [Contract Type Name] ='SOW - Statement of Work'
        """,
        """
        -- 1113 work out deltas delta processing (remove old contract and load delta)
Select * from [dbo].[OneLink_Master_New_FG_Delta] -- 19th delta where [Contract Type Name] ='SOW - Statement of Work'
        """,
        """
        -- 476 delete from orig if exists in delta
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta]) and [Contract Type Name]  ='SOW - Statement of Work'
        """,
        """
        -- (289 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select *, null,'Non-FG',null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]  ='SOW - Statement of Work'
        """,
        """
        -- (476 rows affected) special one off inserts
insert into [OneLink_Master_New_FG_Load] Select *, null,'Non-FG',null,null,null,null,null,null,null,null,null,null from OneLink_Master_New_FG where [Contract Type Name] ='SOW - Statement of Work' and  [External Contract Identifier]='FG_0000000000000000016770'
        """,
        """
        -- 10/14 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241014]) and [Contract Type Name]='SOW - Statement of Work'
        """,
        """
        -- (27 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select *,null,'Non-FG',null,null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241014] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='SOW - Statement of Work'
        """,
        """
        -- (62 rows affected) 10/18 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241018]) and [Contract Type Name]='SOW - Statement of Work'
        """,
        """
        -- (15 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select * ,null,'Non-FG',null,null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241018] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='SOW - Statement of Work'
        """,
        """
        -- (4 rows affected) 10/25 Delta work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_Delta_20241025]) and [Contract Type Name]='SOW - Statement of Work'
        """,
        """
        -- (17 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select * ,null,'Non-FG',null,null,null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_Delta_20241025] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='SOW - Statement of Work'
        """,
        """
        -- (38 rows affected) Additional SOW work
delete from [dbo].[OneLink_Master_New_FG_Load] where [External Contract Identifier] IN (Select [External Contract Identifier] from [dbo].[OneLink_Master_New_FG_AdditionalSOW]) and [Contract Type Name]='SOW - Statement of Work'
        """,
        """
        -- (1 rows affected) then insert from deltas
insert into [dbo].[OneLink_Master_New_FG_Load] select *,'Additional SOW',null,'Non-FG',null,null,null,null,null,null,null,null,null,null,null,null from [dbo].[OneLink_Master_New_FG_AdditionalSOW] d where not exists (Select 'x' from [dbo].[OneLink_Master_New_FG_Load] f where f.[External Contract Identifier]=d.[External Contract Identifier]) and [Contract Type Name]='SOW - Statement of Work'
        """,
        """
        -- (10 rows affected) update FG flag for FG suppliers
update [OneLink_Master_New_FG_Load] set FG='FG' where ltrim(rtrim([Supplier Number])) in (Select ltrim(rtrim([VENDOR_ID])) from FG_EnabledSuppliers) and [Contract Type Name] ='SOW - Statement of Work'
        """,
        """
        -- (1183 rows affected)
select distinct [External Contract Identifier],[Contract #] from [OneLink_Master_New_FG_Load] where [Contract Type Name] ='SOW - Statement of Work' and FG='Non-FG'
        """,
        """
        -- 188 prep load contract file csv with active status for loading JO only (R file) -- AmtLineMax
drop table [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_SOW select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_SOW from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX]
        """,
        """
        -- from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d
from  [dbo].[FG Consumption data Oct26_filtered])d --from [dbo].[FG_LOA-SOW-1018])d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee],[sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        -- (877 rows affected) JO Only -- Consumed Amt
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_SOW select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_SOW from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_RELEASED] from  [dbo].[FG Consumption data Oct26_filtered])d --from [dbo].[FG_LOA-SOW-1018])d
        """,
        """
        -- from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d
pivot ( max([AMT_LINE_RELEASED]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses, [Program Fee]) ) piv;
        """,
        """
        -- (877 rows affected)
alter table [OneLink_Master_New_FG_Load] add [sPro/Legacy Consumed (paid)] nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_expenses nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_programfee nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_TimeandMaterial_managedTeams nvarchar(255) alter table [OneLink_Master_New_FG_Load] add consumed_fixedfeeManagedService nvarchar(255)
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Fixed Fee/Manage Service] ,[Price & Payment Contract Type Custom Field 2]=a.[Time & Material / Managed Teams] ,[Price & Payment Contract Type Custom Field 3]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] ,[Price & Payment Contract Type Custom Field 5]=a.[Program Fee] ,[sPro/Legacy Consumed (paid)] = a.[sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_SOW] a on l.[External Contract Identifier]=a.[CNTRCT_ID] where l.[Contract Type Name] ='SOW - Statement of Work'
        """,
        """
        -- (578 rows affected)
update [OneLink_Master_New_FG_Load] set consumed_fixedfeeManagedService=a.[Fixed Fee/Manage Service] ,consumed_TimeandMaterial_managedTeams=a.[Time & Material / Managed Teams] ,consumed_expenses=a.[Expenses] ,consumed_programfee=a.[Program Fee] from [OneLink_Master_New_FG_Load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_SOW a on l.[External Contract Identifier]=a.[CNTRCT_ID] where l.[Contract Type Name]  ='SOW - Statement of Work'
        """,
        """
        -- (578 rows affected)
update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]='0' where [Price & Payment Contract Type Custom Field 1]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 2]='0' where [Price & Payment Contract Type Custom Field 2]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 3]='0' where [Price & Payment Contract Type Custom Field 3]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 4]='0' where [Price & Payment Contract Type Custom Field 4]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 5]='0' where [Price & Payment Contract Type Custom Field 5]='';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 1]='0' where [Price & Payment Contract Type Custom Field 1] is null ;--'NULL';
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 2]='0' where [Price & Payment Contract Type Custom Field 2] is null ;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 3]='0' where [Price & Payment Contract Type Custom Field 3] is null ;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 4]='0' where [Price & Payment Contract Type Custom Field 4] is null ;
        """,
        """
        update [OneLink_Master_New_FG_Load] set [Price & Payment Contract Type Custom Field 5]='0' where [Price & Payment Contract Type Custom Field 5] is null ;
        """,
        """
        select distinct [Price & Payment Contract Type Custom Field 1] from [OneLink_Master_New_FG_Load]
        """,
        """
        -- gl string
select distinct [Default Account for Supplier Invoice] from  [dbo].[OneLink_Master_New_FG_Load] where [Supplier Number]  in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers]) and updated_contract_# in  ('FG_0000000000000000019159','FG_0000000000000000019161')
        """,
        """
        alter table [dbo].[OneLink_Master_New_FG_Load] add updatedDefaultAccountforSupplierInvoice nvarchar(500); alter table [dbo].[OneLink_Master_New_FG_Load] add cleansedDefaultAccountforSupplierInvoice nvarchar(500) alter table [dbo].[OneLink_Master_New_FG_Load] add invalidGLString nvarchar(20)
        """,
        """
        -- make sure load table has cleansed [Default Account for Supplier Invoice] so we can join to accounts table properly
update [dbo].[OneLink_Master_New_FG_Load] set cleansedDefaultAccountforSupplierInvoice=[Updated Default Account for Supplier Invoice] from [OneLink_Master_New_FG_Load] f inner join [dbo].[GLString_CleanUP Work 20241004] c on ltrim(rtrim(f.[Default Account for Supplier Invoice]))=ltrim(rtrim(c.[Default Account for Supplier Invoice]))
        """,
        """
        -- (2161 rows affected) apply elly updates
update [dbo].[OneLink_Master_New_FG_Load] set cleansedDefaultAccountforSupplierInvoice=[Updated Default Account for Supplier Invoice] from [OneLink_Master_New_FG_Load] f inner join [dbo].[GLString_CleanUP Work 20241004] c on ltrim(rtrim(f.ellyGLString))=ltrim(rtrim(c.[Default Account for Supplier Invoice])) where ellyGLString is not null
        """,
        """
        -- (25 rows affected) for prod
update [dbo].[OneLink_Master_New_FG_Load] set updatedDefaultAccountforSupplierInvoice=g.[Name] from [dbo].[OneLink_Master_New_FG_Load] j inner join [dbo].[AccountMaster_PROD_20241018] g on ltrim(rtrim(j.cleansedDefaultAccountforSupplierInvoice))=ltrim(rtrim(g.[Code]))
        """,
        """
        -- (2099 rows affected) updating to angel when blank
update [dbo].OneLink_Master_New_FG_LOAD set updatedBusinessUser=[Business User*];
        """,
        """
        -- (2141 rows affected) update to Angel
update [dbo].OneLink_Master_New_FG_LOAD set updatedBusinessUser='P529206' from [dbo].OneLink_Master_New_FG_LOAD e where not exists (Select 'x' from [dbo].[coupa_users] u where e.[Business User*]=u.Login and u.Active='Active');
        """,
        """
        -- (70 rows affected) [Engagement Manager]
update [dbo].OneLink_Master_New_FG_LOAD set updatedEngagementManager=[Engagement Manager];
        """,
        """
        -- (2141 rows affected)
update [dbo].OneLink_Master_New_FG_LOAD set updatedEngagementManager='' from [dbo].OneLink_Master_New_FG_LOAD e where  not exists (Select 'x' from [dbo].[coupa_users] u where e.[Engagement Manager]=u.Login and u.Active='Active');
        """,
        """
        -- (242 rows affected) owner login updates update owner logins with replacement
update OneLink_Master_New_FG_LOAD set updatedOwnerLogin=[Owner Login];
        """,
        """
        -- 2141
update OneLink_Master_New_FG_LOAD set updatedOwnerLogin=[Replacement ID] from OneLink_Master_New_FG_LOAD f inner join replacementUsers u on ltrim(rtrim(f.[Owner Login]))=ltrim(rtrim(u.[Old Owner Login]));
        """,
        """
        -- (359 rows affected) create csv for load for SOW's (FG Enabled)
select [Contract Header] ,[Contract Name] ,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://'+[Contract #]+'/'+[Contract #]+'_LA.zip' as [Legal Agreement] ---[Legal Agreement]-- ,[Currency] ,[Source] ,[Supplier Account #] ,updatedOwnerLogin as [updatedOwnerLogin] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'Kaiser Permanente Corporation'  as  [Default Account Type for Supplier Invoice]--'Kaiser Permanente Corporation' ,updatedDefaultAccountforSupplierInvoice as [Default Account for Supplier Invoice] -- updatedDefaultAccountforSupplierInvoice ,[Savings %] ,[Minimum Spend] ,replace([Maximum Spend],',','') as [Maximum Spend] ,[Stop Spend Over Contract Value] ,'Fieldglass' as [Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://'+[Contract #]+'/'+[Contract #]+'_ATT.zip' as [Attachment 1] --[Attachment 1] -- ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,'No' as [Used For Buying] -- all No for FG enabled suppliers ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,isnull([Price & Payment Contract Type Custom Field 1],'0') as [Price & Payment Contract Type Custom Field 1] ,isnull([Price & Payment Contract Type Custom Field 2],'0') as [Price & Payment Contract Type Custom Field 2] ,isnull([Price & Payment Contract Type Custom Field 3],'0') as [Price & Payment Contract Type Custom Field 3] ,isnull([Price & Payment Contract Type Custom Field 4],'0') as [Price & Payment Contract Type Custom Field 4] ,isnull([Price & Payment Contract Type Custom Field 5],'0') as [Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,updatedBusinessUser as [Business User*] , [Engagement Type] ,updatedEngagementManager as[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,case when [Commodity Name] like '%Professional%' then 'Professional Services' else 'Consulting' end as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_load] where [Supplier Number]  in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers]) and [External Contract Identifier] in ('FG_R-00000000000000020770') order by [External Contract Identifier]
        """,
        """
        -- Create CSV for Non FG Enabled JO Non-FG Enabled Suppliers
select [Contract Header] ,[Contract Name] ,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://'+[Contract #]+'/'+[Contract #]+'_LA.zip' as [Legal Agreement] --[Legal Agreement]-- ,[Currency] ,[Source] ,[Supplier Account #] ,updatedOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'Kaiser Permanente Corporation'  as  [Default Account Type for Supplier Invoice]--'Kaiser Permanente Corporation' ,updatedDefaultAccountforSupplierInvoice as [Default Account for Supplier Invoice] -- updatedDefaultAccountforSupplierInvoice ,[Savings %] ,[Minimum Spend] ,replace([Maximum Spend],',','') as [Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://'+[Contract #]+'/'+[Contract #]+'_ATT.zip' as [Attachment 1] --[Attachment 1] -- ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,replace(isnull([Price & Payment Contract Type Custom Field 1],'0'),'','0') as [Price & Payment Contract Type Custom Field 1] ,replace(isnull([Price & Payment Contract Type Custom Field 2],'0'),'','0') as [Price & Payment Contract Type Custom Field 2] ,replace(isnull([Price & Payment Contract Type Custom Field 3],'0'),'','0') as [Price & Payment Contract Type Custom Field 3] ,replace(isnull([Price & Payment Contract Type Custom Field 4],'0'),'','0') as [Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,updatedBusinessUser as [Business User*] ,[Engagement Type] ,updatedEngagementManager as [Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,case when [Commodity Name] like '%Professional%' then 'Professional Services' else 'Consulting' end as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] from OneLink_Master_New_FG_Load where  [External Contract Identifier] in ('0000000000000000000001500','0000000000000000000016361') and [Supplier Number] not in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- create csv for load for SOW's (NON FG Enabled with FG contract #)
select [Contract Header] ,[Contract Name] ,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://'+[Contract #]+'/'+[Contract #]+'_LA.zip' as [Legal Agreement]--[Legal Agreement]-- ,[Currency] ,[Source] ,[Supplier Account #] ,updatedOwnerLogin as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'Kaiser Permanente Corporation'  as  [Default Account Type for Supplier Invoice]--'Kaiser Permanente Corporation' ,updatedDefaultAccountforSupplierInvoice as [Default Account for Supplier Invoice] -- updatedDefaultAccountforSupplierInvoice ,[Savings %] ,[Minimum Spend] ,replace([Maximum Spend],',','') as [Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://'+[Contract #]+'/'+[Contract #]+'_ATT.zip' as [Attachment 1] --[Attachment 1] -- ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,'No' as [Used For Buying] -- all No for FG enabled suppliers ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,[Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,isnull([Price & Payment Contract Type Custom Field 1],'0') as [Price & Payment Contract Type Custom Field 1] ,isnull([Price & Payment Contract Type Custom Field 2],'0') as [Price & Payment Contract Type Custom Field 2] ,isnull([Price & Payment Contract Type Custom Field 3],'0') as [Price & Payment Contract Type Custom Field 3] ,isnull([Price & Payment Contract Type Custom Field 4],'0') as [Price & Payment Contract Type Custom Field 4] ,isnull([Price & Payment Contract Type Custom Field 5],'0') as [Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,updatedBusinessUser as [Business User*] , [Engagement Type] ,updatedEngagementManager as[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,case when [Commodity Name] like '%Professional%' then 'Professional Services' else 'Consulting' end as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_load] where [Supplier Number] not in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers]) and [External Contract Identifier]  in ('FG_0000000000000000015984') order by [External Contract Identifier]
        """,
        """
        -- these LOA's are closed contracts who has an active counterpart.. move this to python script so it can move documents try new version. first get all contracts that have 2 versions G -- find contracts whose FG version only was sent
select distinct SUBSTRING(replace(replace([Contract #],'FG_',''),'OL_',''), PATINDEX('%[^0]%', replace(replace([Contract #],'FG_',''),'OL_','')) , LEN(replace(replace([Contract #],'FG_',''),'OL_',''))) as Matched_Contract_# ,[Contract #], updated_contract_#, updated_contract_status, Expires into [dbo].[OneLink_Master_New_FG_ContractNumbers_LOA] from [dbo].[OneLink_Master_New_FG] where filename ='G_2024-05-30' and ltrim(rtrim([Supplier Number])) In (Select distinct ltrim(rtrim([Vendor id])) from FG_EnabledSuppliers) and cast(expires as date)>'2024-01-31'
        """,
        """
        Select * from [OneLink_Master_New_FG_ContractNumbers_R] where Matched_Contract_# in (select Matched_Contract_# from [dbo].[OneLink_Master_New_FG_ContractNumbers_R] group by Matched_Contract_# having count(*)>1)
        """,
        """
        -- create a table with master contract number,new contract number and old contract number
select matched_contract_#, isnull(updated_contract_#,replace([Contract #],'OL_','')) as New_Contract_Number into [dbo].[OneLink_Master_New_FG_ContractNumberMaster_R] from [dbo].[OneLink_Master_New_FG_ContractNumbers_R] where updated_contract_# like 'FG%'
        """,
        """
        update [OneLink_Master_New_FG_ContractNumberMaster_R] set Old_Contract_Number=isnull(updated_contract_#,replace([Contract #],'OL_','')) from [OneLink_Master_New_FG_ContractNumberMaster_R] a inner join [OneLink_Master_New_FG_ContractNumbers_R] b on a.matched_contract_#=b.matched_contract_# where updated_contract_# not like 'FG%'
        """,
        """
        select * from [OneLink_Master_New_FG_ContractNumberMaster_R] where old_contract_number is null order by matched_contract_#
        """,
        """
        -- prep load contract file csv with active status for loading JO only (R file) -- AmtLineMax
drop table [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX] from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee],[sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        -- (1009 rows affected) JO Only -- Consumed Amt
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_RELEASED] from [dbo].FG_AdditionalInformation_FGEnabledSuppliers)d pivot ( max([AMT_LINE_RELEASED]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses, [Program Fee])
        """,
        """
        ) piv;
        """,
        """
        -- 1009 *********** pending check how to populate final released amount field ********* update load table with additional custom fields so we can export load file 1. pick JO as first pass with complex logic
select * from [OneLink_Master_New_FG_R_Load] a where updated_contract_# in ('FG_0000000000000000004600','FG_0000000000000000006266','FG_0000000000000000007439','FG_0000000000000000015410' ,'FG_0000000000000000015593','FG_0000000000000000016815','FG_0000000000000000018687','FG_0000000000000000018711','FG_0000000000000000018782' ,'FG_0000000000000000018815','FG_0000000000000000019188','FG_0000000000000000019646','FG_0000000000000000020289')
        """,
        """
        drop table [OneLink_Master_New_FG_Delta_load]
        """,
        """
        -- run update on custom fields
select * into [OneLink_Master_New_FG_Delta_load] from [OneLink_Master_New_FG_Delta]
        """,
        """
        alter table [OneLink_Master_New_FG_R_Load] add [sPro/Legacy Consumed (paid)] nvarchar(255) alter table [OneLink_Master_New_FG_R_Load] add expenses nvarchar(255) alter table [OneLink_Master_New_FG_R_Load] add consumed_programfee nvarchar(255) alter table [OneLink_Master_New_FG_R_Load] add consumed_TimeandMaterial_managedTeams nvarchar(255) alter table [OneLink_Master_New_FG_R_Load] add consumed_fixedfeeManagedService nvarchar(255)
        """,
        """
        alter table [OneLink_Master_New_FG_Delta_load] add [sPro/Legacy Consumed (paid)] nvarchar(255) alter table [OneLink_Master_New_FG_Delta_load] add consumed_expenses nvarchar(255) alter table [OneLink_Master_New_FG_Delta_load] add consumed_programfee nvarchar(255) alter table [OneLink_Master_New_FG_Delta_load] add consumed_TimeandMaterial_managedTeams nvarchar(255) alter table [OneLink_Master_New_FG_Delta_load] add consumed_fixedfeeManagedService nvarchar(255)
        """,
        """
        update [OneLink_Master_New_FG_R_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Fixed Fee/Manage Service] ,[Price & Payment Contract Type Custom Field 2]=a.[Time & Material / Managed Teams] ,[Price & Payment Contract Type Custom Field 3]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] ,[Price & Payment Contract Type Custom Field 5]=a.[Program Fee] ,[sPro/Legacy Consumed (paid)] = a.[sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_R_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB] a on l.[External Contract Identifier]=a.[CNTRCT_ID]
        """,
        """
        update [OneLink_Master_New_FG_Delta_load] set [Price & Payment Contract Type Custom Field 1]=a.[Fixed Fee/Manage Service] ,[Price & Payment Contract Type Custom Field 2]=a.[Time & Material / Managed Teams] ,[Price & Payment Contract Type Custom Field 3]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] ,[Price & Payment Contract Type Custom Field 5]=a.[Program Fee] ,[sPro/Legacy Consumed (paid)] = a.[sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_Delta_load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB] a on l.[External Contract Identifier]=a.[CNTRCT_ID]
        """,
        """
        update [OneLink_Master_New_FG_R_Load] set consumed_fixedfeeManagedService=a.[Fixed Fee/Manage Service] ,consumed_TimeandMaterial_managedTeams=a.[Time & Material / Managed Teams] ,consumed_expenses=a.[Expenses] ,consumed_programfee=a.[Program Fee] from [OneLink_Master_New_FG_R_Load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Consumed_JOB a on l.[updated_contract_#]=a.[CNTRCT_ID]
        """,
        """
        update [OneLink_Master_New_FG_Delta_load] set consumed_fixedfeeManagedService=a.[Fixed Fee/Manage Service] ,consumed_TimeandMaterial_managedTeams=a.[Time & Material / Managed Teams] ,consumed_expenses=a.[Expenses] ,consumed_programfee=a.[Program Fee] from [OneLink_Master_New_FG_Delta_load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Consumed_JOB a on l.[External Contract Identifier]=a.[CNTRCT_ID]
        """,
        """
        -- looks for old counterparts
Select * from [OneLink_Master_New_FG_ContractNumberMaster_R] where  New_Contract_Number in ('FG_0000000000000000004600','FG_0000000000000000006266','FG_0000000000000000007439','FG_0000000000000000015410' ,'FG_0000000000000000015593','FG_0000000000000000016815','FG_0000000000000000018687','FG_0000000000000000018711','FG_0000000000000000018782' ,'FG_0000000000000000018815','FG_0000000000000000019188','FG_0000000000000000019646','FG_0000000000000000020289')
        """,
        """
        -- gl string
select distinct [Default Account for Supplier Invoice] from  [dbo].[OneLink_Master_New_FG_R_Load] where [Supplier Number]  in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers]) and updated_contract_# in  ('FG_0000000000000000019159','FG_0000000000000000019161')
        """,
        """
        alter table [dbo].[OneLink_Master_New_FG_R_Load] add updatedDefaultAccountforSupplierInvoice nvarchar(500)
        """,
        """
        alter table [dbo].[OneLink_Master_New_FG_Delta_load] add updatedDefaultAccountforSupplierInvoice nvarchar(500)
        """,
        """
        update [dbo].[OneLink_Master_New_FG_R_Load] set updatedDefaultAccountforSupplierInvoice=Concatenated_Result from [dbo].[OneLink_Master_New_FG_R_Load] j inner join [dbo].[FG_GLLookUp_Master] g on ltrim(rtrim(j.[Default Account for Supplier Invoice]))=ltrim(rtrim(g.[Default Account for Supplier Invoice]))
        """,
        """
        update [OneLink_Master_New_FG_Delta_load] set updatedDefaultAccountforSupplierInvoice=Concatenated_Result from [dbo].[OneLink_Master_New_FG_Delta_load] j inner join [dbo].[FG_GLLookUp_Master] g on ltrim(rtrim(j.[Default Account for Supplier Invoice]))=ltrim(rtrim(g.[Default Account for Supplier Invoice]))
        """,
        """
        -- now build export csv create csv for load for JO's
select [Contract Header] ,[Contract Name]
        """,
        """
        -- ,replace([Contract #],'OL_','') as [Contract #] -- this is for FG enabled supplier only
,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,replace([Parent Contract Number],'OL_','') as [Parent Contract Number] ,'' as [Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,'file://'+[Contract #]+'/'+[Contract #]+'_LA.zip' as [Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,'G294578' as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'Kaiser Permanente Corporation' as [Default Account Type for Supplier Invoice] ,'' as [Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,'file://'+[Contract #]+'/'+[Contract #]+'_ATT.zip' as [Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,'No' as [Used For Buying] -- all No for FG enabled suppliers ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,'JO - Job Order' as [Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,isnull([Price & Payment Contract Type Custom Field 1],'') as [Price & Payment Contract Type Custom Field 1] ,isnull([Price & Payment Contract Type Custom Field 2],'') as [Price & Payment Contract Type Custom Field 2] ,isnull([Price & Payment Contract Type Custom Field 3],'') as [Price & Payment Contract Type Custom Field 3] ,isnull([Price & Payment Contract Type Custom Field 4],'') as [Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,'G294578' as [Business User*] , [Engagement Type] ,'G294578' as[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,'Consulting' as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_load]--[dbo].[OneLink_Master_New_FG_R_Load] where [Supplier Number]  in (Select [VENDOR_ID] from [dbo].[FG_EnabledSuppliers]) and [External Contract Identifier] in ('FG_0000000000000000004600','FG_0000000000000000004785','FG_0000000000000000004843','FG_0000000000000000006200','FG_0000000000000000006266','FG_0000000000000000003248','FG_0000000000000000008624','FG_0000000000000000008820','FG_0000000000000000008871','FG_0000000000000000008972','FG_0000000000000000009168','FG_0000000000000000009227','FG_0000000000000000009521','FG_0000000000000000009744','FG_0000000000000000009749','FG_0000000000000000009752','FG_0000000000000000009900','FG_0000000000000000009901','FG_0000000000000000009952','FG_0000000000000000009979')-- non FG JO
        """,
        """
        -- "sPro Legacy Consumed Amount =$1,790,498.65 || Fixed Fee/Managed Services Consumed Amount =$0.00 || T&M/Managed Teams Consumed Amount =$70,573.44 || Expenses Consumed Amount =$1,706.42 || Program Fee Consumed Amount =$394.54" CAMP BOWIE SERVICE CTR [0315]-Po/Ho Corp [30000]-National PBCK Admin [7477]-Management Training [81105] CAMP BOWIE SERVICE CTR [0315]-Po/Ho Corp [30000]-National PBCK Admin [7477]-Management Training [81105]
select * from [dbo].[OneLink_Master_New_FG_B_LOAD] where [Contract #] like '%11460%'
        """,
        """
        select distinct [External Contract Identifier],updatedDefaultAccountforSupplierInvoice , [Default Account for Supplier Invoice] from [dbo].[OneLink_Master_New_FG_Delta_load] where [External Contract Identifier] in ('FG_0000000000000000019646','0000000000000000000021183')
        """,
        """
        select distinct [External Contract Identifier],updatedDefaultAccountforSupplierInvoice , [Default Account for Supplier Invoice] from [dbo].[OneLink_Master_New_FG_R_load] where [External Contract Identifier] in ('FG_0000000000000000019646','0000000000000000000021183')
        """,
        """
        -- create csv for load for SOW
select [Contract Header] ,[Contract Name]
        """,
        """
        -- ,replace([Contract #],'OL_','') as [Contract #] -- this is for FG enabled supplier only
,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,replace([Parent Contract Number],'OL_','') as [Parent Contract Number] ,'' as [Parent Contract Name] ,[Supplier Name] ,[Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,'G294578' as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,'Kaiser Permanente Corporation' as [Default Account Type for Supplier Invoice] ,updatedDefaultAccountforSupplierInvoice as [Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,'No' as [Used For Buying] -- all No for FG enabled suppliers ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,'' as [Published Date] ,'' as [Execution Date] ,[Department Name] ,'JO - Job Order' as [Contract Type Name] ,isnull([Contract Type Custom Field 1],0) as [Contract Type Custom Field 1] ,isnull([Contract Type Custom Field 2],0) as [Contract Type Custom Field 2] ,isnull([Contract Type Custom Field 3],0) as [Contract Type Custom Field 3] ,isnull([Contract Type Custom Field 4],0) as [Contract Type Custom Field 4] ,isnull([Contract Type Custom Field 5],0) as [Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,isnull([Price & Payment Contract Type Custom Field 1],'') as [Price & Payment Contract Type Custom Field 1] ,isnull([Price & Payment Contract Type Custom Field 2],'') as [Price & Payment Contract Type Custom Field 2] ,isnull([Price & Payment Contract Type Custom Field 3],'') as [Price & Payment Contract Type Custom Field 3] ,isnull([Price & Payment Contract Type Custom Field 4],'') as [Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,'G294578' as [Business User*] , [Engagement Type] ,'G294578' as[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,'Consulting' as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([consumed_expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO**/ as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_Delta_load] where [Supplier Number]  in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers]) and [External Contract Identifier] ='FG_0000000000000000013526' --in ('0000000000000000000021201','FG_21178','0000000000000000000021166'
        """,
        """
        -- ,'0000000000000000000021188') non FG JO "sPro Legacy Consumed Amount =$3,304,113.42 || Fixed Fee/Managed Services Consumed Amount =$0.00 || T&M/Managed Teams Consumed Amount =$0.00 || Expenses Consumed Amount =$0.00 || Program Fee Consumed Amount =$0.00" run updates
select distinct [Contract Header] ,[Contract Name]
        """,
        """
        -- ,replace([Contract #],'OL_','') as [Contract #] -- this is for FG enabled supplier only
,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,'Kaiser Permanente Corporation' as [Default Account Type for Supplier Invoice] ,updatedDefaultAccountforSupplierInvoice as [Default Account for Supplier Invoice] from [dbo].[OneLink_Master_New_FG_R_Load] where [Supplier Number]  in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers]) and [External Contract Identifier] in ('FG_0000000000000000019646','FG_0000000000000000018815')
        """,
        """
        update [OneLink_Master_New_FG] set filename ='G_2024-05-30' where filename is null delete from [OneLink_Master_New_FG] where [Contract Header] IN ('Contract Party','Contract Party Contact')
        """,
        """
        select * from [dbo].[OneLink_Master_New_FG] -- where [Contract #] like '%12968' select * from FG_AdditionalInformation --where [CNTRCT_ID] like '%12968'
        """,
        """
        select * from [FG_JO_MSOW]
        """,
        """
        alter table [OneLink_Master_New_FG] add  updated_contract_# nvarchar(255)
        """,
        """
        alter table [OneLink_Master_New_FG] add  updated_parent_contract_# nvarchar(255)
        """,
        """
        alter table [OneLink_Master_New_FG] add  updated_contract_status nvarchar(255)
        """,
        """
        -- update FG table from file Meena sent for contract #, parent contract #
update [OneLink_Master_New_FG] set updated_contract_#= m.[CNTRCT_ID], updated_parent_contract_#= m.[PARENT_CONTR_ID],updated_contract_status=m.[CNTRCT_STATUS] from [OneLink_Master_New_FG] o inner join [dbo].[FG_JO_MSOW] m on o.[External Contract Identifier]=m.[CNTRCT_ID]
        """,
        """
        -- 659
select * from [OneLink_Master_New_FG] where updated_contract_status is null
        """,
        """
        update [OneLink_Master_New_FG] set updated_contract_status ='NA' where updated_contract_status is null
        """,
        """
        -- create FG Enabled Supplier Only Table
insert into  FG_AdditionalInformation_FGEnabledSuppliers select * from FG_AdditionalInformation where [VENDOR_ID] in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        drop table [OneLink_Master_New_FG_B_Load] select * into [dbo].[OneLink_Master_New_FG_B_Load] from [dbo].[OneLink_Master_New_FG] where filename='B_2024-05-30' and updated_contract_status IN ('NA','A') and cast(expires as date)>'2024-01-31'
        """,
        """
        -- 56
drop table [OneLink_Master_New_FG_R_Load] select * into [dbo].[OneLink_Master_New_FG_R_Load] from [dbo].[OneLink_Master_New_FG] where  filename='R_2024-05-30' and updated_contract_status IN ('NA','A') and cast(expires as date)>'2024-01-31'
        """,
        """
        -- 273
select distinct [Contract Type Name] from [OneLink_Master_New_FG_R_Load] -- JOB
        """,
        """
        select distinct [Contract Type Name] from [OneLink_Master_New_FG_B_Load] -- MSOW
        """,
        """
        -- count of contracts
select count(distinct [Contract #]) from OneLink_Master_New_FG where  filename='B_2024-05-30' and updated_contract_status='A'
        """,
        """
        -- 63 MSOW
select count(distinct [Contract #]) from OneLink_Master_New_FG where  filename='R_2024-05-30' and updated_contract_status='A'
        """,
        """
        -- 328 JO
Select count(distinct [Contract #]) from [OneLink_Master_New_FG] where filename='G_2024-05-30' and [Supplier Number] IN (Select distinct [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- 50 LOA
Select count(distinct [Contract #]) from [OneLink_Master_New_FG] where filename='D_2024-05-30' and [Supplier Number] IN (Select distinct [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- 854 SOW
select distinct updated_contract_status from OneLink_Master_New_FG_B_Load
        """,
        """
        select distinct updated_contract_status from OneLink_Master_New_FG where filename='B_2024-05-30' and updated_contract_status='C'
        """,
        """
        -- find same contract with FG and non-FG versions
select * from [dbo].[OneLink_Master_New_FG] where [Contract #] like '%18815%'
        """,
        """
        -- R -- find contracts whose FG version only was sent
drop table  [dbo].[OneLink_Master_New_FG_ContractNumbers_R]
        """,
        """
        select distinct SUBSTRING(replace(replace([Contract #],'FG_',''),'OL_',''), PATINDEX('%[^0]%', replace(replace([Contract #],'FG_',''),'OL_','')) , LEN(replace(replace([Contract #],'FG_',''),'OL_',''))) as Matched_Contract_# ,[Contract #], updated_contract_#, updated_contract_status,Expires into [dbo].[OneLink_Master_New_FG_ContractNumbers_R] from [dbo].[OneLink_Master_New_FG] where filename ='R_2024-05-30' and ltrim(rtrim([Supplier Number])) In (Select distinct ltrim(rtrim([Vendor id])) from FG_EnabledSuppliers) and cast(Expires as date)> '2024-01-31'
        """,
        """
        -- where [Contract #] like '%18815%' 480
Select * from [OneLink_Master_New_FG_ContractNumbers_R] where Matched_Contract_# in (select Matched_Contract_# from [dbo].[OneLink_Master_New_FG_ContractNumbers_R] group by Matched_Contract_# having count(*)=1) and [Contract #] like '%FG%'
        """,
        """
        -- 56 rows -- 13 with FG filter
drop table  [dbo].[OneLink_Master_New_FG_ContractNumbers_B]
        """,
        """
        -- B -- find contracts whose FG version only was sent
select distinct SUBSTRING(replace(replace([Contract #],'FG_',''),'OL_',''), PATINDEX('%[^0]%', replace(replace([Contract #],'FG_',''),'OL_','')) , LEN(replace(replace([Contract #],'FG_',''),'OL_',''))) as Matched_Contract_# ,[Contract #], updated_contract_#, updated_contract_status, Expires into [dbo].[OneLink_Master_New_FG_ContractNumbers_B] from [dbo].[OneLink_Master_New_FG] where filename ='B_2024-05-30' and ltrim(rtrim([Supplier Number])) In (Select distinct ltrim(rtrim([Vendor id])) from FG_EnabledSuppliers) and cast(expires as date)>'2024-01-31'
        """,
        """
        -- 96
Select * from [OneLink_Master_New_FG_ContractNumbers_B] where Matched_Contract_# in (select Matched_Contract_# from [dbo].[OneLink_Master_New_FG_ContractNumbers_B] group by Matched_Contract_# having count(*)=1) and [Contract #] like '%FG%'
        """,
        """
        -- 27 rows -- 8 with FG filter
select * from [dbo].[OneLink_Master_New_FG_ContractNumbers_R] where Matched_Contract_# like '%13703%'
        """,
        """
        -- like '%12128%'
select distinct expires from [dbo].OneLink_Master_New_FG where [Contract #]
        """,
        """
        -- inactive vendor report
truncate table coupa_suppliers
        """,
        """
        select * from COUPA_Suppliers
        """,
        """
        select * from OneLink_Master_New_FG f where not exists (Select 'x' from COUPA_Suppliers c where f.[Supplier Number]=c.[Supplier #] and c.Status='active')
        """,
        """
        select distinct f.[Supplier Number],c.Status from OneLink_Master_New_FG f left join COUPA_Suppliers c on f.[Supplier Number]=c.[Supplier #] where isnull(c.Status,'inactive') IN ('inactive','draft')
        """,
        """
        select distinct filename,count(*) from  OneLink_Master_New_FG group by filename
        """,
        """
        select distinct VENDOR_ID, name1 as Venodr_Name, VENDOR_STATUS as OL_Status, 'Not In COUPA' as COUPA_Status, replacement_vendor from OL_Supplier_Master where VENDOR_ID in ('100012126','100016617','100039638')
        """,
        """
        select * from COUPA_Suppliers where [Supplier #] in ('100071723','100197915','100209245')
        """,
        """
        Select 'Contract Header' as [Contract Header],[Contract Name],[External Contract Identifier] as [contract #],[Hierarchy Type],'Published' as [Status] from OneLink_Master_New_FG_load where [External Contract Identifier] in ('0000000000000000000018924','0000000000000000000019343','0000000000000000000021036','0000000000000000000021131' ,'0000000000000000000021144','0000000000000000000021460','0000000000000000000021531','0000000000000000000021532','FG_0000000000000000010868','FG_0000000000000000014148' ,'FG_0000000000000000014924','FG_0000000000000000017579','FG_0000000000000000018548','FG_0000000000000000018619','FG_0000000000000000020454','FG_16819-1' ,'FG_21129')
        """,
        """
        -- update expiry date for the LOA
Select 'Contract Header' as [Contract Header],[Contract Name],[External Contract Identifier] as [contract #],[Hierarchy Type],'2024-06-21' as [Expires] from OneLink_Master_New_FG_load where [External Contract Identifier] ='0000000000000000000021180'
        """,
        """
        -- update expiry date for the MSOW
Select 'Contract Header' as [Contract Header],[Contract Name],[External Contract Identifier] as [contract #],[Hierarchy Type],[Expires] from OneLink_Master_New_FG_load where [External Contract Identifier] In ()
        """,
        """
        -- update contract type and term type for LOA
Select 'Contract Header' as [Contract Header],[Contract Name],[External Contract Identifier] as [contract #],[Hierarchy Type] ,'Perpetual' as [Term Type] ,'' as [Expires] from OneLink_Master_New where [External Contract Identifier] like '%4161-4895%'
        """,
        """
        -- update contract type and term type for LOA
Select 'Contract Header' as [Contract Header],[Contract Name],[External Contract Identifier] as [contract #],[Hierarchy Type] ,'Perpetual' as [Term Type] ,'' as [Expires] from coupa_contracts where [Contract #] like '%4161-4895%'
        """,
        """
        -- JO Updtaes
drop table [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB_UATUpd from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX] from [dbo].[FG_consumption_UAT_contracts])d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee],[sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        -- (56 rows affected) JO Only -- Consumed Amt
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB_UATUpd select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB_UATUpd from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_RELEASED] from [dbo].[FG_consumption_UAT_contracts])d pivot ( max([AMT_LINE_RELEASED]) for [DESCR60] in ([Fixed Fee/Manage Service],[Time & Material / Managed Teams],Expenses, [Program Fee])
        """,
        """
        ) piv;
        """,
        """
        -- 56 rows
update [OneLink_Master_New_FG_R_Load] set consumed_fixedfeeManagedService=a.[Fixed Fee/Manage Service] ,consumed_TimeandMaterial_managedTeams=a.[Time & Material / Managed Teams] ,consumed_expenses=a.[Expenses] ,consumed_programfee=a.[Program Fee] from [OneLink_Master_New_FG_R_Load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB_UATUpd a on l.[External Contract Identifier]=a.[CNTRCT_ID]
        """,
        """
        update [OneLink_Master_New_FG_Delta_load] set [Price & Payment Contract Type Custom Field 1]=a.[Fixed Fee/Manage Service] ,[Price & Payment Contract Type Custom Field 2]=a.[Time & Material / Managed Teams] ,[Price & Payment Contract Type Custom Field 3]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] ,[Price & Payment Contract Type Custom Field 5]=a.[Program Fee] ,[sPro/Legacy Consumed (paid)] = a.[sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_Delta_load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB_UATUpd] a on l.[External Contract Identifier]=a.[CNTRCT_ID]
        """,
        """
        -- 12
update  [dbo].[OneLink_Master_New_FG_Delta_load] set consumed_fixedfeeManagedService=a.[Fixed Fee/Manage Service] ,consumed_TimeandMaterial_managedTeams=a.[Time & Material / Managed Teams] ,consumed_expenses=a.[Expenses] ,consumed_programfee=a.[Program Fee] from [dbo].[OneLink_Master_New_FG_Delta_load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_JOB_UATUpd a on l.[External Contract Identifier]=a.[CNTRCT_ID]
        """,
        """
        update [OneLink_Master_New_FG_R_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Fixed Fee/Manage Service] ,[Price & Payment Contract Type Custom Field 2]=a.[Time & Material / Managed Teams] ,[Price & Payment Contract Type Custom Field 3]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] ,[Price & Payment Contract Type Custom Field 5]=a.[Program Fee] ,[sPro/Legacy Consumed (paid)] = a.[sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_R_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB_UATUpd] a on l.[External Contract Identifier]=a.[CNTRCT_ID]
        """,
        """
        select * from [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_JOB_UATUpd] where  [CNTRCT_ID] like '%18687' select * from [dbo].[FG_consumption_UAT_contracts] where  [CNTRCT_ID]  like '%18687' select * from [dbo].[OneLink_Master_New_FG_R_Load] where  [External Contract Identifier] like '%18687' "sPro Legacy Consumed Amount =$1,790,498.65 || Fixed Fee/Managed Services Consumed Amount =$0.00 || T&M/Managed Teams Consumed Amount =$598,460.18 || Expenses Consumed Amount =$28,053.81 || Program Fee Consumed Amount =$3,445.83" "sPro Legacy Consumed Amount =$133,112.00 || Fixed Fee/Managed Services Consumed Amount =$366,058.00 || T&M/Managed Teams Consumed Amount =$0.00 || Expenses Consumed Amount =$0.00 || Program Fee Consumed Amount =$2,013.32"
        """,
        """
        -- MSOW prep load contract file csv with active status for loading MSOW only (B file) -- AmtLineMax
drop table [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW_UATUpd select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW_UATUpd from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX] from [dbo].[FG_consumption_UAT_contracts] )d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([Hybrid/Uncategorized],[Time & Material / Managed Teams],Expenses,Contingency,[Program Fee]) ) piv;
        """,
        """
        -- (56 rows affected) MSOW Only -- Consumed Amt ([sPro/Legacy Consumed (paid)])
drop table FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW_SPro_UATUpd select * into [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW_SPro_UATUpd from (Select [CNTRCT_ID],[VENDOR_ID],[DESCR60],[AMT_LINE_MAX] from [dbo].[FG_consumption_UAT_contracts])d pivot ( max([AMT_LINE_MAX]) for [DESCR60] in ([sPro/Legacy Consumed (paid)]) ) piv;
        """,
        """
        -- 56
update [OneLink_Master_New_FG_B_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Hybrid/Uncategorized] ,[Price & Payment Contract Type Custom Field 2]=a.[Time & Material / Managed Teams] ,[Price & Payment Contract Type Custom Field 3]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] ,[Price & Payment Contract Type Custom Field 5]=a.[Program Fee] from [OneLink_Master_New_FG_B_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW_UATUpd] a on l.[updated_contract_#]=a.[CNTRCT_ID]
        """,
        """
        -- 44
update [OneLink_Master_New_FG_B_Load] set [Price & Payment sPro Pre-Consumed/FG Consumed amount] = [sPro/Legacy Consumed (paid)] from [OneLink_Master_New_FG_B_Load] l inner join [dbo].FG_AdditionalInformation_FGEnabledSuppliers_Released_MSOW_SPro_UATUpd a on l.[updated_contract_#]=a.[CNTRCT_ID] where  [Supplier Number] in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- 44
select * from [dbo].[FG_consumption_UAT_contracts] where [CNTRCT_ID] like '%6998%'
        """,
        """
        "sPro Legacy Consumed Amount =$67,311,423.85"
        """,
        """
        select * from [dbo].[FG_Consumption] where [External SOW ID]  in ('FG_0000000000000000007439','FG_0000000000000000018815')
        """,
        """
        select distinct [External Contract Identifier] ,[Price & Payment sPro Pre-Consumed/FG Consumed amount],[sPro/Legacy Consumed (paid)] ,[expenses],[consumed_programfee],[consumed_TimeandMaterial_managedTeams],[consumed_fixedfeeManagedService] from [dbo].[OneLink_Master_New_FG_R_Load] where [External Contract Identifier] in ('FG_0000000000000000007439','FG_0000000000000000018815')
        """,
        """
        update [OneLink_Master_New_FG_B_Load] set [Price & Payment Contract Type Custom Field 1]=a.[Hybrid/Uncategorized] ,[Price & Payment Contract Type Custom Field 2]=a.[Expenses] ,[Price & Payment Contract Type Custom Field 3]=a.[Program Fee] ,[Price & Payment Contract Type Custom Field 4]=a.[Contingency] from [OneLink_Master_New_FG_B_Load] l inner join [dbo].[FG_AdditionalInformation_FGEnabledSuppliers_AmtLineMax_MSOW_UATUpd] a on l.[updated_contract_#]=a.[CNTRCT_ID] where [Supplier Number] in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers])
        """,
        """
        -- 44
select [Contract Header] ,[Contract Name]
        """,
        """
        -- ,replace([Contract #],'OL_','') as [Contract #] -- this is for FG enabled supplier only
,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type]
        """,
        """
        ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull(consumed_fixedfeeManagedService,'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull(consumed_TimeandMaterial_managedTeams,'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull(consumed_expenses,'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull(consumed_programfee,'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_R_Load] where [Supplier Number]  in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers]) and [External Contract Identifier]--='FG_0000000000000000018687' in ('FG_0000000000000000006266','FG_0000000000000000007439','FG_0000000000000000015593','FG_0000000000000000018782' ,'FG_0000000000000000018815','FG_0000000000000000019188','FG_0000000000000000019646','FG_0000000000000000020289','FG_0000000000000000018687' ,'FG_0000000000000000016815','FG_0000000000000000018711','FG_0000000000000000015410')
        """,
        """
        "sPro Legacy Consumed Amount =$3,304,113.42 || Fixed Fee/Managed Services Consumed Amount =$0.00 || T&M/Managed Teams Consumed Amount =$123,496.32 || Expenses Consumed Amount =$0.00 || Program Fee Consumed Amount =$679.30" "sPro Legacy Consumed Amount =$133,112.00 || Fixed Fee/Managed Services Consumed Amount =$366,058.00 || T&M/Managed Teams Consumed Amount =$0.00 || Expenses Consumed Amount =$0.00 || Program Fee Consumed Amount =$2,013.32" "sPro Legacy Consumed Amount =$1,790,498.65 || Fixed Fee/Managed Services Consumed Amount =$0.00 || T&M/Managed Teams Consumed Amount =$598,460.18 || Expenses Consumed Amount =$28,053.81 || Program Fee Consumed Amount =$3,445.83"
        """,
        """
        select distinct [Contract Header] ,[Contract Name]
        """,
        """
        -- ,replace([Contract #],'OL_','') as [Contract #] -- this is for FG enabled supplier only
,[External Contract Identifier] as [Contract #] ,'Contract' as [Hierarchy Type] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([sPro/Legacy Consumed (paid)],'') as float),'C') +' || Fixed Fee/Managed Services Consumed Amount ='+FORMAT(cast(isnull([consumed_fixedfeeManagedService],'') as float),'C') +' || T&M/Managed Teams Consumed Amount ='+FORMAT(cast(isnull([consumed_TimeandMaterial_managedTeams],'') as float),'C') +' || Expenses Consumed Amount ='+FORMAT(cast(isnull([expenses],'') as float),'C') +' || Program Fee Consumed Amount ='+FORMAT(cast(isnull([consumed_programfee],'') as float),'C') +'"'  -- this concat is for SOW, LOA and JO from [dbo].[OneLink_Master_New_FG_R_Load] where [Supplier Number]  in (Select [Vendor id] from [dbo].[FG_EnabledSuppliers]) and [External Contract Identifier] in ('FG_0000000000000000007439','FG_0000000000000000018815')
        """,
        """
        update [OneLink_Master_New_FG_R_Load] set [consumed_TimeandMaterial_managedTeams]='533971.52',[expenses]='2977.29',[consumed_programfee]='2943.43' where [External Contract Identifier] = 'FG_0000000000000000007439'
        """,
        """
        update [OneLink_Master_New_FG_R_Load] set [consumed_TimeandMaterial_managedTeams]='98749.44',[expenses]=null,[consumed_programfee]='5431.55' where [External Contract Identifier] = 'FG_0000000000000000018815'
        """,
        """
        select * from /**
        """,
        """
        -- 7439
T&M = 533971.52 Expenses = 2977.29 Program Fee = 2943.43
        """,
        """
        -- 18815
T&M = 98749.44 Expenses = Program Fee = 5431.55
        """,
        """
        **/
        """,
        """
        -- MSOW comsumption upd
select [Contract Header] ,[Contract Name]
        """,
        """
        -- ,replace([Contract #],'OL_','') as [Contract #] -- this is for FG enabled supplier only
,[External Contract Identifier] as [Contract #] ,case when [Contract Type Name]='MSOW - Master Statement of Work' then 'Master' else 'Contract' end as [Hierarchy Type] ,[Price & Payment Contract Type Custom Field 3] ,'"'+'sPro Legacy Consumed Amount =' +FORMAT(cast(isnull([Price & Payment sPro Pre-Consumed/FG Consumed amount],'') as float),'C')+'"' as [Price & Payment sPro Pre-Consumed/FG Consumed amount] from [dbo].[OneLink_Master_New_FG_B_Load] where [External Contract Identifier] in ('FG_0000000000000000010258','FG_0000000000000000010989','FG_0000000000000000011460','FG_0000000000000000011690','FG_0000000000000000011740' ,'FG_0000000000000000012123','FG_0000000000000000012664','FG_0000000000000000012686','FG_0000000000000000013316','FG_0000000000000000013331','FG_0000000000000000013341' ,'FG_0000000000000000013369','FG_0000000000000000013371','FG_0000000000000000013372','FG_0000000000000000013373','FG_0000000000000000013374' ,'FG_0000000000000000013376','FG_0000000000000000013386','FG_0000000000000000013387','FG_0000000000000000016173','FG_0000000000000000017390' ,'FG_0000000000000000017767','FG_0000000000000000020406','FG_0000000000000000003248','FG_0000000000000000003477','FG_0000000000000000003478','FG_0000000000000000006479' ,'FG_0000000000000000006709','FG_0000000000000000006998','FG_0000000000000000008258','FG_0000000000000000008613','FG_0000000000000000008629')
        """,
        """
        select * from OneLink_Master_New where [Contract #] like '%rx%' [Contract Type Name] like '%pharmacy%'
        """,
        """
        select f.[Contract #],f.[Default Account for Supplier Invoice],a.[Name  UAT] from [dbo].[OneLink_Master_New_FG_R_Load] f left join [dbo].[OneLink_Accounts List_UAT_09112024] a on replace(f.[Default Account for Supplier Invoice],' ','') =a.[Segment 1*]+'-'+a.[Segment 2]+'-'+a.[Segment 3]+'-'+a.[Segment 4]+'-'+a.[Segment 5]+'-'+[Segment 6]+'-'+[Segment 7]
        """,
        """
        -- 0315-30000-7477-81105
select distinct [Default Account for Supplier Invoice] from [OneLink_Master_New_FG_R_Load] select * from [dbo].[OneLink_Accounts List_UAT_09112024] select * from [dbo].[OneLink_Accounts List_PROD_09112024]
        """,
        """
        -- 0315-30000-7477-81105
select f.[Contract #],f.[Default Account for Supplier Invoice],a.[Name PROD] from [dbo].[OneLink_Master_New_FG_R_Load] f left join [dbo].[OneLink_Accounts List_PROD_09112024] a on replace(f.[Default Account for Supplier Invoice],' ','') =a.[Segment 1*]+'-'+a.[Segment 2]+'-'+a.[Segment 3]+'-'+a.[Segment 4]+'-'+a.[Segment 5]+'-'+[Segment 6]+'-'
        """,
        """
        -- Meena and I established we have to use the lookup files for this pupose (Build a GL Lookup Master)
select * from [dbo].[FG_GLLookUp_GLUnitLocDept] where [External Ref Code] in ('0315|30000|7477')
        """,
        """
        -- 0315-30000-7477-81105
select * from [dbo].[OneLink_Master_New_FG_R_Load] where [Default Account for Supplier Invoice]='0315-30000-7477-81105- - -' and replace([Contract #],'OL_','') in ('FG_0000000000000000006266','FG_0000000000000000007439','FG_0000000000000000015593','FG_0000000000000000018782' ,'FG_0000000000000000018815','FG_0000000000000000019188','FG_0000000000000000019646','FG_0000000000000000020289','FG_0000000000000000018687','FG_0000000000000000016815' ,'FG_0000000000000000018711','FG_0000000000000000015410')
        """,
        """
        -- OL_FG_0000000000000000019159 OL_FG_0000000000000000019161
SELECT distinct [Concatenated_Result] FROM [KP_CON].[dbo].[FG_GLLookUp_Master]
        """,
        """
        update [KP_CON].[dbo].[FG_GLLookUp_Master] set [Concatenated_Result]= replace([Concatenated_Result],'- -','')
        """,
        """
        -- Consulting Fees-Reportable [77750]
update [KP_CON].[dbo].[FG_GLLookUp_Master] set [Concatenated_Result]= ltrim(rtrim([Concatenated_Result]))
        """,
        """
        -- cannot blindly update - .. have to only replace the end of the string
select [Concatenated_Result], right(ltrim(rtrim([Concatenated_Result])),1) FROM [KP_CON].[dbo].[FG_GLLookUp_Master] where right(ltrim(rtrim([Concatenated_Result])),1)='-'
        """,
        """
        -- check contracts that need updating
select distinct c.[Contract #],c.[Default Account Type for Supplier Invoice],c.[Used For Buying] ,o.[Default Account Type for Supplier Invoice] ,c.[Default Account for Supplier Invoice],o.[Default Account for Supplier Invoice] from coupa_contracts c left join OneLink_Master_New o on c.[Contract #]=o.[Contract #]
        """,
        """
        -- where c.[Contract #] ='OL_10471'
where c.[Contract #] like 'OL%' and c.[Hierarchy Type]  IN ('Contract') and o.[Default Account for Supplier Invoice]<>''
        """,
        """
        -- test one update
select 'Contract Header' as [Contract Header],[Contract Name],[Contract #],[Hierarchy Type],'Kaiser Permanente Corporation' as [Default Account Type for Supplier Invoice]
        """,
        """
        -- ,'--NULL--' ,'KFHP COLORADO [1608]-Franklin Medical Offices [16002]-Cat Scan [0847]-O/S Other Misc Services [78675]'
as [Default Account for Supplier Invoice]
        """,
        """
        -- ,'KF HEALTHPLAN NORTHWEST [1008]-North Interstate [10702]-Outside Dental Laboratory [4301]-O/S Purchases Services-Dental [78695]' as [Default Account for Supplier Invoice] ,expires,[Termination Reason Code],[Contract Type Name] ,'KP INFORMATION TECHNOLOGY [9601]-KPIT ADMIN [30100]-ITO IPS STI SCL [8158]-Other Miscellaneous Expense [81675]-KP Information Technology [KT001]-KPIT Cloud Computing [KT08576]' ,'THE PERM MED GRP [0206]-San Leandro Hospital [20451]-Radiology-Interventional [0833]-O/S Other Misc Services [78675]'
from coupa_contracts where [Contract #]='OL_10833'
        """,
        """
        -- 1008-10702-4301-78695- - -   (for OL_10021) 9601-30100-8388-76780-KT001-KT15768- (for OL_10619) 9601-30100-8158-81675-KT001-KT08576- (for OL_10471) 0206-20451-0833-78675- - - (f0r OL_03-10291_consign) 1608-16002-0847-78675- - -(OL_10833)
select * from [dbo].[GLString_GLUnit_Loc_Dept_Prod] where [External Ref Code]='1608|16002|0847'
        """,
        """
        -- KF HEALTHPLAN NORTHWEST [1008]
select * from [dbo].[GLString_Account_Prod] where [External Ref Code]='78675'
        """,
        """
        select * from [dbo].[GLString_PCBusinessUnit_Prod] where [External Ref Code]='KT001|KT08576'
        """,
        """
        -- create master table of all gl string codes to generate the descriptions
Select distinct [Default Account for Supplier Invoice] from OneLink_Master_New where [Default Account for Supplier Invoice]<>''
        """,
        """
        select * from coupa_contracts where [Parent Contract Number]='OL_10471'
        """,
        """
        KP INFORMATION TECHNOLOGY [9601]-KPIT ADMIN [30100]-ITO WNS WANLAN LCOM [8626]-Expendable Equipment [76825]-KP Information Technology [KT001]-SCAL LAN LIFECYCLE MAINTENANCE [KT13641]
        """,
        """
        select * from OneLink_Master_New where [Default Account for Supplier Invoice] like '%9601%30100%8626%76825%KT001%KT13641%'
        """,
        """
        -- uat test
select 'Contract Header' as [Contract Header],[Contract Name],[Contract #],[Hierarchy Type],'Kaiser Permanente Corporation' as [Default Account Type for Supplier Invoice] ,'KP INFORMATION TECHNOLOGY [9601]-KPIT ADMIN [30100]-ITI INV IMG [8932]-Expendable Equipment [76825]-KP Information Technology [KT001]-Network Segmentation Capabilit [KT31502]'
        """,
        """
        -- ,'KP INFORMATION TECHNOLOGY [9601]-KPIT ADMIN [30100]-ITO WNS WANLAN LCOM [8626]-Expendable Equipment [76825]-KP Information Technology [KT001]-SCAL LAN LIFECYCLE MAINTENANCE [KT13641]'
as [Default Account for Supplier Invoice] from OneLink_Master_New where [Contract #]='OL_18552'
        """,
        """
        select * from [dbo].[Missing_Suppliers-Contracts_Not_In_COUPA_08272024-WW Comments_tab1] a where exists (Select 'x' from coupa_contracts c where ltrim(rtrim(c.[Contract #]))=ltrim(rtrim(a.[Contract #])) )
        """,
        """
        select a.[Contract Type Name],a.[Contract #],a.expires,e.expires as Enriched_Expires,a.[Supplier Number],e.[Supplier Number] as Enriched_SupplierNumber ,[NAME1] as OL_Name,[VENDOR_STATUS] as OL_Status ,[Comments] as Wendy_Comments,[Elevate Comments, if not delivered],[CLM Team Comments]
        """,
        """
        -- ,r.[ReplacementVendorID]
from [dbo].[Missing_Suppliers-Contracts_Not_In_COUPA_08272024-WW Comments_tab1] a left join [dbo].[EnrichedContracts_Master] e on ltrim(rtrim(e.[Contract #]))=ltrim(rtrim(a.[Contract #])) left join COUPA_Suppliers s on ltrim(rtrim(e.[Supplier Number]))=ltrim(rtrim(case when s.[Supplier Number]='' then 'NA' else s.[Supplier Number] end)) left join [dbo].[Elevate Migration Tracker_20240609] e1 on ltrim(rtrim(e1.[Contract #]))=ltrim(rtrim(a.[Contract #])) left join [dbo].[OL_Supplier_Master] o on ltrim(rtrim(e.[Supplier Number]))=ltrim(rtrim(o.[VENDOR_ID]))
        """,
        """
        -- left join ReplacementVendors r on ltrim(rtrim(a.[Supplier Number]))=ltrim(rtrim(r.[Vendor Id])) zero so removed
where s.Name is null order by 1,2
        """,
        """
        select a.*,e.expires as Enriched_Expires,[Elevate Comments, if not delivered],[CLM Team Comments]
        """,
        """
        -- ,e.[Supplier Number] as Enriched_SupplierNumber--,e.[Supplier Name] as Enriched_SupplierName a.[Contract #],a.expires,e.expires as Enriched_Expires,a.[Supplier Number],e.[Supplier Number] as Enriched_SupplierNumber,s.Name as COUPA_SupplierName ,r.[ReplacementVendorID]
from [dbo].[Missing_Suppliers-Contracts_Not_In_COUPA_08272024-WW Comments_tab2] a left join [dbo].[EnrichedContracts_Master] e on ltrim(rtrim(e.[Contract #]))=ltrim(rtrim(a.[Contract #])) left join COUPA_Suppliers s on ltrim(rtrim(e.[Supplier Name]))=ltrim(rtrim(s.Name)) left join [dbo].[Elevate Migration Tracker_20240609] e1 on ltrim(rtrim(e1.[Contract #]))=ltrim(rtrim(a.[Contract #]))
        """,
        """
        -- left join [dbo].[OL_Supplier_Master] o on ltrim(rtrim(a.))=ltrim(rtrim(o.[VENDOR_ID])) left join ReplacementVendors r on ltrim(rtrim(a.[Supplier Number]))=ltrim(rtrim(r.[Vendor Id])) zero so removed
where s.Name is null order by 1,2
        """,
        """
        update [dbo].[OneLink_Contract_Union] set [Replacement Vendor ID]=null,final_vendor=null
        """,
        """
        -- (11137 rows affected) truncate table Wave2_Missing_Suppliers
update [dbo].[OneLink_Contract_Union] set [Replacement Vendor ID]=ltrim(rtrim(r.[Replacement ID])) from [dbo].[OneLink_Contract_Union] o inner join [dbo].[ReplacementVendors20240408] r on ltrim(rtrim(o.[Supplier Number]))=ltrim(rtrim(r.[VENDOR_ID]))
        """,
        """
        -- 216
update [dbo].[OneLink_Contract_Union] set final_vendor=case when [Replacement Vendor ID] is null then ltrim(rtrim([Supplier Number])) when [Replacement Vendor ID] ='' then ltrim(rtrim([Supplier Number])) else ltrim(rtrim([Replacement Vendor ID])) end
        """,
        """
        select distinct filename,[Contract Type Name]--,[Supplier Number],[Replacement Vendor ID],[final_vendor] from [dbo].[OneLink_Contract_Union] where [Supplier Number]=''
        """,
        """
        -- get supplier id, name, OL Status, COUPA status for the 124 missing supplier in recon summary get suppliers that do not exists at all in coupa truncate table Wave2_Missing_Suppliers truncate table OneLink_Contract_Union_Wave2
insert into  OneLink_Contract_Union_Wave2 Select distinct ltrim(rtrim(final_vendor)) as final_vendor,'Does not exist in COUPA' as COUPA_STATUS from OneLink_Contract_Union o where ltrim(rtrim(o.[Contract Type Name])) IN ('MSA - Master Services Agreement' ,'MPRODS - Master Products/Services Agreement','SOW - Statement of Work','Services Agreement','ConSignA - Consignment Agreement' ,'DSA - Data Sharing Agreement','SWLA - Software License Agreement','EQUIPMA - Equipment Maintenanc','TECH - Technology Evaluation Agreement' ,'VOF - Vendor Order Form','SEA - Single Entity Agreement','NSA - National Supplier Agreement','PPA - Participant Plan Agreement')
        """,
        """
        -- (1908 rows affected)
insert into Wave2_Missing_Suppliers select distinct ltrim(rtrim(final_vendor)),'Does not exist in COUPA' from OneLink_Contract_Union_Wave2 w where not exists (Select 'X' from [dbo].[COUPA_Suppliers] c where ltrim(rtrim(w.final_vendor))=ltrim(rtrim(c.[Supplier #])))
        """,
        """
        -- (75 rows affected) get suppliers that exists in coupa but are inactive
insert into  Wave2_Missing_Suppliers Select distinct ltrim(rtrim(final_vendor)),'Inactive' from OneLink_Contract_Union_Wave2 o where  exists (Select 'X' from [dbo].[COUPA_Suppliers] c where ltrim(rtrim(o.final_vendor))=ltrim(rtrim(c.[Supplier #])) and status='inactive')
        """,
        """
        -- 7 report to mdm team
Select distinct v.Final_Vendor as Supplier_Number, o.NAME1 as Supplier_Name ,o.VENDOR_STATUS as OL_Vendor_Status,v.Reason as Coupa_Vendor_Status from Wave2_Missing_Suppliers v left join [dbo].[OL_Supplier_Master] o on ltrim(rtrim(v.Final_Vendor))=ltrim(rtrim(o.VENDOR_ID))
        """,
        """
        -- 82 buid out OL contract union table
Select distinct [Contract #],[Contract Name],[Contract Type Name],starts, expires,[Supplier Number],[Supplier Name] ,null as replacement_vendor_id,null as final_vendor into OneLink_Master_Union_Full_Wave2 from (Select distinct [Contract #],[Contract Name],[Contract Type Name],starts, expires,[Supplier Number],[Supplier Name] from [dbo].[OneLink_Master_New] where ltrim(rtrim([Contract Type Name])) IN ('MSA - Master Services Agreement' ,'MPRODS - Master Products/Services Agreement','SOW - Statement of Work','Services Agreement','ConSignA - Consignment Agreement' ,'DSA - Data Sharing Agreement','SWLA - Software License Agreement','EQUIPMA - Equipment Maintenanc','TECH - Technology Evaluation Agreement' ,'VOF - Vendor Order Form','SEA - Single Entity Agreement','NSA - National Supplier Agreement','PPA - Participant Plan Agreement') union Select distinct [Contract #],[Contract Name],[Contract Type Name],starts, expires,[Supplier Number],[Supplier Name] from [dbo].[OneLink_Master_Delta_Full] where ltrim(rtrim([Contract Type Name])) IN ('MSA - Master Services Agreement' ,'MPRODS - Master Products/Services Agreement','SOW - Statement of Work','Services Agreement','ConSignA - Consignment Agreement' ,'DSA - Data Sharing Agreement','SWLA - Software License Agreement','EQUIPMA - Equipment Maintenanc','TECH - Technology Evaluation Agreement' ,'VOF - Vendor Order Form','SEA - Single Entity Agreement','NSA - National Supplier Agreement','PPA - Participant Plan Agreement') union Select distinct 'OL_'+RIGHT([CNTRCT_ID],(LEN([CNTRCT_ID])-PATINDEX('%[^0]%', [CNTRCT_ID])+1)) as [Contract #] ,'',case [KP_RQST_TYPE2] when 'A' then 'MSA - Master Services Agreement' when 'D' then 'SOW - Statement of Work' when 'N' then'SEA - Single Entity Agreement' when 'M' then 'Services Agreement' when 'O' then 'SWLA - Software License Agreement' when 'P' then 'TECH - Technology Evaluation Agreement' when 'S' then 'MPRODS - Master Products/Services Agreement' when 'V' then 'DSA - Data Sharing Agreement' when 'W' then 'EQUIPMA - Equipment Maintenanc' when 'Y' then 'ConSignA - Consignment Agreement' when 'Z' then 'VOF - Vendor Order Form' when 'G' then 'LOA - Letter of Agreement' end as [Contract Type Name] ,[TO_CHAR(A CNTRCT_BEGIN_DT,'YYYY-MM-DD')] as starts, [TO_CHAR(A CNTRCT_EXPIRE_DT,'YYYY-MM-DD')] as expires,[VENDOR_ID],'' from [dbo].[OneLink_Master_Delta] where case [KP_RQST_TYPE2] when 'A' then 'MSA - Master Services Agreement' when 'D' then 'SOW - Statement of Work' when 'N' then'SEA - Single Entity Agreement' when 'M' then 'Services Agreement' when 'O' then 'SWLA - Software License Agreement' when 'P' then 'TECH - Technology Evaluation Agreement' when 'S' then 'MPRODS - Master Products/Services Agreement' when 'V' then 'DSA - Data Sharing Agreement' when 'W' then 'EQUIPMA - Equipment Maintenanc' when 'Y' then 'ConSignA - Consignment Agreement' when 'Z' then 'VOF - Vendor Order Form' when 'G' then 'LOA - Letter of Agreement' end IN ('MSA - Master Services Agreement' ,'MPRODS - Master Products/Services Agreement','SOW - Statement of Work','Services Agreement','ConSignA - Consignment Agreement' ,'DSA - Data Sharing Agreement','SWLA - Software License Agreement','EQUIPMA - Equipment Maintenanc','TECH - Technology Evaluation Agreement' ,'VOF - Vendor Order Form','SEA - Single Entity Agreement','NSA - National Supplier Agreement','PPA - Participant Plan Agreement') ) a
        """,
        """
        -- (5631 rows affected)
update OneLink_Master_Union_Full_Wave2 set replacement_vendor_id=null, final_vendor=null
        """,
        """
        -- add replacement vendor id
update OneLink_Master_Union_Full_Wave2 set replacement_vendor_id =r.[Replacement ID] from OneLink_Master_Union_Full_Wave2 o inner join [dbo].[ReplacementVendors20240408] r on ltrim(rtrim(o.[Supplier Number]))=ltrim(rtrim(r.[VENDOR_ID]))
        """,
        """
        -- 121 update final vendor
update OneLink_Master_Union_Full_Wave2 set final_vendor =r.[Replacement ID] from OneLink_Master_Union_Full_Wave2 o inner join [dbo].[ReplacementVendors20240408] r on o.[Supplier Number]=r.[VENDOR_ID]
        """,
        """
        -- 121
update OneLink_Master_Union_Full_Wave2 set final_vendor = [Supplier Number] where final_vendor is null or final_vendor=''
        """,
        """
        select distinct [Supplier Number],final_vendor from OneLink_Master_Union_Full_Wave2
        """,
        """
        alter table OneLink_Master_Union_Full_Wave2 add SupplierName nvarchar(255)
        """,
        """
        update OneLink_Master_Union_Full_Wave2 set SupplierName=s.[NAME1] from OneLink_Master_Union_Full_Wave2 o inner join [dbo].[OL_Supplier_Master] s on o.final_vendor=s.[VENDOR_ID]
        """,
        """
        -- filtered down report for Wendy
Select distinct [Contract #],[Contract Name],[Contract Type Name],starts, expires,[Supplier Number],[SupplierName] from [dbo].[OneLink_Master_Union_Full_Wave2] o where exists (Select 'X' from [dbo].[Wave2_Missing_Suppliers] w where ltrim(rtrim(o.final_vendor))=ltrim(rtrim(w.final_vendor)))
        """,
        """
        select * from COUPA_Suppliers where [Supplier #]='100219560' select * from [dbo].[OneLink_Master_Union_Full_Wave2] where [Supplier Number]='100219560'
        """,
        """
        select * from [coupa_paymentTerms]
        """,
        """
        select distinct [Updated Payment Terms] from [Enrichment of Payment term_Phase 2&3_20240606_v2]
        """,
        """
        update [dbo].[Enrichment of Payment term_Phase 2&3_20240606_v2] set [Updated Payment Terms]=replace([Updated Payment Terms],';','')
        """,
        """
        -- replace([Updated Payment Terms],'Dis ','') ltrim(rtrim([Updated Payment Terms]))--replace([Updated Payment Terms],'Discount ','') --replace([Updated Payment Terms],'DiscountNet','Net')
where [Updated Payment Terms]='1.5% 30  NET 30 '
        """,
        """
        select distinct [CurrentContractID],[COUPA  Payment Terms (Values  10, 15, 20, 30, 45, 60, 90, 120)] as PaymentTerm ,v1.[Contract Name],v1.[Contract Type Name],v1.final_supplier,v1.starts,v1.expires,v1.Description,v1.[Commodity Name] from [dbo].[Vizient_Payment_Rebates_20240112] v left join [Prod_U_2024-04-22_Load] v1 on v.[CurrentContractID]=v1.[Contract #] where [COUPA  Payment Terms (Values  10, 15, 20, 30, 45, 60, 90, 120)] not in ('1% 30 Net 45','1.5% 30 Net 30','2% 10 Net 45','2% 15 Net 30','2% 15 Net 45','Net 10','Net 15','Net 20','Net 25','Net 30','Net 35','Net 45','Net 60','Net 90','2% 15 Net 60','2.5% 15 Net 60','2.75% 30 Net 30','2% 12 Net 42','Net 5')
        """,
        """
        -- and [COUPA  Payment Terms (Values  10, 15, 20, 30, 45, 60, 90, 120)]<>'NULL'
select distinct [Contract #],[Payment Terms],[Updated Payment Terms],[Contract Type],[Supplier ID],[Supplier Name]
        """,
        """
        -- ,v1.[Contract Name],v1.[Contract Type Name],v1.final_supplier,v1.starts,v1.expires,v1.Description,v1.[Commodity Name]
from [dbo].[Enrichment of Payment term_Phase 2&3_20240606_v2] o --left join [Prod_U_2024-04-22_Load] v1 on o.[Contract #]=v1.[Contract #] where ltrim(rtrim([Updated Payment Terms])) not in ('1% 30 Net 45','1.5% 30 Net 30','2% 10 Net 45','2% 15 Net 30','2% 15 Net 45','Net 10','Net 15','Net 20','Net 25','Net 30','Net 35','Net 45','Net 60','Net 90','2% 15 Net 60','2.5% 15 Net 60','2.75% 30 Net 30','2% 12 Net 42','Net 5')
        """,
        """
        -- and  ltrim(rtrim([Updated Payment Terms]))<>'' update from overall PT master I created for blank PT
update coupa_contracts_PT_report set [Payment Terms]=p.[Updated Payment Terms] from coupa_contracts_PT_report c left join [Enrichment of Payment term_Phase 2&3_20240606_v2] p on c.[Contract #]=p.[Contract #] where c.[Payment Terms]=''
        """,
        """
        update coupa_contracts_PT_report set [Payment Terms]=p.[Updated Payment Terms] from coupa_contracts_PT_report c left join [Enrichment of Payment term_Phase 2&3_20240606_v2] p on c.[Contract #]=p.[Contract #] where c.[Payment Terms] is null
        """,
        """
        -- update PT from mercedes file do it in excel (lookup) payment terms load for terms available in coupa
drop table coupa_contract_paymentTerms_ToLoad
        """,
        """
        -- first filter out amendments & contracts that have payment terms populated OL Only (blank PT and non-amendment hierarchy type)
Select distinct 'Contract Header' as Contract_Header,[Contract Name],[Contract #],[Hierarchy Type],[Payment Terms],'OL_Contracts' as Source, [Parent Contract Number]
        """,
        """
        -- into coupa_contract_paymentTerms_ToLoad_1
from coupa_contracts where [Payment Terms]='' and [Contract #] like 'OL_%' and [Hierarchy Type] IN ('Contract','Master')
        """,
        """
        -- 6910 Viz Only
insert into coupa_contract_paymentTerms_ToLoad_1 Select distinct 'Contract Header',[Contract Name],[Contract #],[Hierarchy Type],[Payment Terms] , 'Viz_Contracts' ,[Parent Contract Number] from coupa_contracts where [Payment Terms]='' and [Contract Type Name] IN ('VSA - Vizient Standalone Agreement','VMA - Vizient Master Agreement','VPA - Vizient Product Agreement') and [Hierarchy Type] IN ('Contract','Master')
        """,
        """
        -- 1046 CAH Only
insert into coupa_contract_paymentTerms_ToLoad_1 Select distinct 'Contract Header',[Contract Name],[Contract #],[Hierarchy Type],[Payment Terms], 'CareAtHome', [Parent Contract Number] from coupa_contracts where [Payment Terms]='' and [Contract #] like 'CAH_%' and [Hierarchy Type] IN ('Contract','Master')
        """,
        """
        -- 1306
select * from [dbo].[coupa_contracts_PT_report]
        """,
        """
        -- now remove parents whose children have been amended.. DO NOT WANT TO TOUCH THEM?? (ASK MEENA IF I COULD UPDATE THEM)
Select * from coupa_contract_paymentTerms_ToLoad_1 where [Contract #] in (Select [Parent Contract Number] from coupa_contracts where [Hierarchy Type]='Amendment')
        """,
        """
        -- 784
delete from coupa_contract_paymentTerms_ToLoad_1 where [Contract #] in (Select [Parent Contract Number] from coupa_contracts where [Hierarchy Type]='Amendment')
        """,
        """
        -- 784
select * from coupa_contract_paymentTerms_ToLoad_1
        """,
        """
        -- update pt from elevate data
update coupa_contract_paymentTerms_ToLoad_1 set [Payment Terms]=p2.[Payment Terms] from coupa_contract_paymentTerms_ToLoad_1 p1 inner join [dbo].[COUPA Contracts with Payment Terms 07-17-2024] p2 on p1.[Contract #]=p2.[Contract #]
        """,
        """
        -- (8478 rows affected)
select [Contract_Header],[Contract Name],[Contract #],[Hierarchy Type],ltrim(rtrim([Payment Terms])) as [Payment Terms] from coupa_contract_paymentTerms_ToLoad_1 where ltrim(rtrim([Payment Terms])) in (Select ltrim(rtrim(code)) from [dbo].[coupa_paymentTerms])
        """,
        """
        -- LOA for elevate to enrich
select * from [dbo].[1682 LOA Missing PT] a where not exists (Select 'x' from [dbo].[PaymentTerms_BK_2024-07-16_rv5_MatchOnContractagainstMercedes] b where a.[Contract #]=b.[Contract #])
        """,
        """
        -- Prod Vizient Delta Process
alter table [dbo].[Prod_Vizient_Delta] add filename nvarchar(255)
        """,
        """
        select * from [dbo].[Prod_Vizient_Delta]
        """,
        """
        delete from [dbo].[Prod_Vizient_Delta] where [Contract Header] IN ('Contract Party','Contract Party Contact')
        """,
        """
        -- (2 rows affected)
update [dbo].[Prod_Vizient_Delta] set filename = 'T_2024-05-06' where filename is null
        """,
        """
        -- 15 find batches that have delta (3 and 8 do not have Delta)
select distinct l.batch from [dbo].[Prod_T_2024-04-19_Load] l inner join [dbo].[Prod_Vizient_Delta] d on ltrim(rtrim(d.[Contract #]))=ltrim(rtrim(l.[Contract #]))
        """,
        """
        Select * from [dbo].[dbo].[Prod_T_2024-04-19_Load] where [Contract #]='KP80406' select * from [dbo].[Prod_Vizient_Delta] where [Contract #]='KP80406'
        """,
        """
        -- prep deltas for load add all new fields needed
alter table [dbo].[Prod_Vizient_Delta] add vizient_updated_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_Vizient_Delta] add replacement_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_Vizient_Delta] add final_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_Vizient_Delta] add  [Parties KP Legal Entity] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_Vizient_Delta] add [Financial Commitment] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_Vizient_Delta] add [Updated_Owner_Login] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_Vizient_Delta] add [Updated_Business_User] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_Vizient_Delta] add [Updated_Commodity_Name] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_Vizient_Delta] add Batch nvarchar(255)
        """,
        """
        -- 1. Supplier Checks/Updates
update [dbo].[Prod_Vizient_Delta] set vizient_updated_supplier=null
        """,
        """
        -- vizient updated supplier
update [dbo].[Prod_Vizient_Delta] set vizient_updated_supplier=ltrim(rtrim(case when v.[Replacement]='' then v.[Search OL ID with Vizient TIN] else v.[Replacement] end)) from [dbo].[Prod_Vizient_Delta] o inner join [dbo].[Task906129_final_Vizient_active_contracts_20240430] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- (14 rows affected)
update [dbo].[Prod_Vizient_Delta] set vizient_updated_supplier='100008941' where vizient_updated_supplier='10008941'
        """,
        """
        -- replacement
update [dbo].[Prod_Vizient_Delta] set replacement_supplier=ltrim(rtrim(r.[Replacement ID])) from [dbo].[Prod_Vizient_Delta] o inner join [dbo].[ReplacementVendors20240408] r on ltrim(rtrim(o.[Supplier Number]))=ltrim(rtrim(r.Vendor_Id))
        """,
        """
        -- (0 rows affected) final_supplier
update [dbo].[Prod_Vizient_Delta] set final_supplier=case when replacement_supplier is null then [Supplier Number] else replacement_supplier end
        """,
        """
        -- (15 rows affected)
update [dbo].[Prod_Vizient_Delta] set final_supplier=case isnull(vizient_updated_supplier,'') when '' then final_supplier else vizient_updated_supplier end
        """,
        """
        -- (15 rows affected)
select distinct final_supplier,vizient_updated_supplier,replacement_supplier,[Supplier Number] from [dbo].[Prod_Vizient_Delta] --null, ''
        """,
        """
        -- check if in coupa
Select c.[Contract #],[Supplier Number] --, Batch from [dbo].[Prod_Vizient_Delta] c --inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where  not exists (Select 'X' from [dbo].[coupa_suppliers] s where c.final_supplier=s.[Supplier #] and s.status='active')
        """,
        """
        -- 12 2. update owner login, business user, Engagement Manager, published and execution date,[Offshore Service Addendum Required?] onwer login
update [dbo].[Prod_Vizient_Delta] set [Updated_Owner_Login]= case [Owner Login] when 'D725503' then 'Y816499' when 'M044247' then 'A807108' when 'M582400' then 'Y245840' when 'Q444093' then 'T368292' when 'Y813310' then 'I263172' when 'Z758670' then	'B719287' else [Owner Login] end;
        """,
        """
        -- business user
update [dbo].[Prod_Vizient_Delta] set [updated_business_user]=Updated_owner_login;
        """,
        """
        -- (15 rows affected) Engagement Manager
update [dbo].[Prod_Vizient_Delta] set [Engagement Manager]='';
        """,
        """
        -- (15 rows affected)
update [dbo].[Prod_Vizient_Delta] set  [Offshore Service Addendum Required?]='No';
        """,
        """
        -- (15 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Default Account for Supplier Invoice]='';
        """,
        """
        -- (15 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Published Date]='',[Execution Date]='';
        """,
        """
        -- (15 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Financial Commitment]='No reportable financial commitment and/or contract term is under 1 year';
        """,
        """
        -- (15 rows affected) 4. update hierarchy type
select distinct [Contract Type Name],[Hierarchy Type] from [UAT_T_2024-03-22] update [dbo].[Prod_Vizient_Delta] set [Hierarchy Type]='Contract' where [Contract Type Name] IN ('VPA - Vizient Product Agreement','VSA - Vizient Standalone Agreement');
        """,
        """
        -- 5. update contract type custom fields
update [dbo].[Prod_Vizient_Delta] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N';
        """,
        """
        update [dbo].[Prod_Vizient_Delta] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y';
        """,
        """
        update [dbo].[Prod_Vizient_Delta] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N';
        """,
        """
        update [dbo].[Prod_Vizient_Delta] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y';
        """,
        """
        update [dbo].[Prod_Vizient_Delta] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N';
        """,
        """
        update [dbo].[Prod_Vizient_Delta] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y';
        """,
        """
        update [dbo].[Prod_Vizient_Delta] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N';
        """,
        """
        update [dbo].[Prod_Vizient_Delta] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y';
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select * --distinct [Contract Type Custom Field 8] from [dbo].[Prod_Vizient_Delta] where [Contract Type Custom Field 8]='';
        """,
        """
        -- ****there is a blank in 1 contract.. CHECK WITH MEENA Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [dbo].[Prod_Vizient_Delta]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
select distinct [Contract Details Contract Type Custom Field 1] from [Prod_Vizient_Delta] update [dbo].[Prod_Vizient_Delta] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO';
        """,
        """
        -- Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [dbo].[Prod_Vizient_Delta]
        """,
        """
        -- update legal entity from vizient file check if all contracts exist in ccl
select * from [dbo].[Prod_Vizient_Delta] o where not  exists (select 'X' from [dbo].[CCL-April2024-103328] v where ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])))
        """,
        """
        -- KP81754
select distinct left(o.[Contract #],2),v.[Contract Type] from [dbo].[Prod_Vizient_Delta] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- where left(o.[Contract #],2)='BM'
select distinct [Contract ID],[Contract Type] from [dbo].[CCL-April2024-103328] where [Contract ID]='KP81754'
        """,
        """
        update  [dbo].[Prod_Vizient_Delta] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' from [dbo].[Prod_Vizient_Delta] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- (303 rows affected) checked against MB missing file
update  [dbo].[Prod_Vizient_Delta] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' where [Parties KP Legal Entity] is null
        """,
        """
        -- (21 rows affected)
select distinct [Parties KP Legal Entity] from [dbo].[Prod_Vizient_Delta]
        """,
        """
        -- update batch
update  [dbo].[Prod_Vizient_Delta] set batch= b.[Batch] from [Prod_Vizient_Delta] o inner join [dbo].[Prod_T_VizientContractsMaster] b on o.[Contract #]=b.[Folder Name]
        """,
        """
        -- done till here 6. update commodity from Meena's file
select distinct [Commodity Name],updated_commodity_name
        """,
        """
        -- ,charindex('-',[Commodity Name]),SUBSTRING([Commodity Name],(charindex('-',[Commodity Name])+1),len([Commodity Name]))
from [dbo].[Prod_Vizient_Delta_T]
        """,
        """
        update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_Vizient_Delta] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[Commodity Name]
        """,
        """
        -- (13 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_Vizient_Delta] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[DESCR60] where [Updated_Commodity_Name] is null
        """,
        """
        -- (2 rows affected) one off updates
update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]='"Bed, Stretcher and Patient Equipment"' where [Commodity Name]='10553-Bed  Stretcher and Patent Care';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment - Patient Lifts"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment - Patient Lifts';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]='"Heating, Ventilating and Air Conditioning - HVAC"' where [Updated_Commodity_Name]='Heating, Ventilating and Air Conditioning - HVAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]='"Housekeeping Uniforms, Gowns and Linens"' where [Updated_Commodity_Name]='Housekeeping Uniforms, Gowns and Linens';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]='"Move, Add, Change - MAC"' where [Updated_Commodity_Name]='Move, Add, Change - MAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]='"Parking, Valet and Shuttle Services"' where [Updated_Commodity_Name]='Parking, Valet and Shuttle Services';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_Vizient_Delta] set [Updated_Commodity_Name]=ltrim(rtrim([Updated_Commodity_Name]))
        """,
        """
        select distinct [Updated_Commodity_Name],[Commodity Name] from  [dbo].[Prod_Vizient_Delta] where [Updated_Commodity_Name] is null
        """,
        """
        -- find contracts that exists in orginal
select distinct [Contract #]-- into Prod_Vizient_Orig_Deltas_T from [dbo].[Prod_Vizient_Delta_T] d where  exists (Select 'X' from [dbo].[Prod_T_2024-04-19_Load] l where ltrim(rtrim(d.[Contract #]))=ltrim(rtrim(l.[Contract #])))
        """,
        """
        -- (13 rows affected) delete delta contracts from original table
delete from [dbo].[Prod_T_2024-04-19_Load] where ltrim(rtrim([Contract #])) IN (Select distinct ltrim(rtrim([Contract #])) from Prod_Vizient_Orig_Deltas_T)
        """,
        """
        -- (13 rows affected) add deltas into original table
insert into [dbo].[Prod_T_2024-04-19_Load] select * from [dbo].[Prod_Vizient_Delta_T] where ltrim(rtrim([Contract #])) IN (Select distinct ltrim(rtrim([Contract #])) from Prod_Vizient_Orig_Deltas_T)
        """,
        """
        -- (13 rows affected) update batch again
update  [dbo].[Prod_T_2024-04-19_Load] set batch= b.[Batch] from [Prod_T_2024-04-19_Load] o inner join [dbo].[Prod_T_VizientContractsMaster] b on o.[Contract #]=b.[Folder Name]
        """,
        """
        -- (324 rows affected)
select distinct batch from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- manuall move attachments from delta to load folders
select distinct [Contract #],batch from [dbo].[Prod_Vizient_Delta_T] where ltrim(rtrim([Contract #])) IN (Select distinct ltrim(rtrim([Contract #])) from Prod_Vizient_Orig_Deltas_T) order by batch
        """,
        """
        -- (13 rows affected) export script for new contracts in delta table
select [Contract Header] ,[Contract Name] ,[Contract #] ,[Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[final_supplier] as [Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,[Updated_Owner_Login] as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,[Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,[Published Date] ,[Execution Date] ,[Department Name] ,[Contract Type Name] ,[Contract Type Custom Field 1] ,[Contract Type Custom Field 2] ,[Contract Type Custom Field 3] ,[Contract Type Custom Field 4] ,[Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,[Price & Payment Contract Type Custom Field 1] ,[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,[Updated_Business_User] as [Business User*] ,[Engagement Type] ,[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,updated_commodity_name as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,[Parties KP Legal Entity] ,[Financial Commitment] from [dbo].[Prod_Vizient_Delta] d where not exists (Select 'X' from [dbo].[Prod_T_2024-04-19_Load] l where ltrim(rtrim(d.[Contract #]))=trim(rtrim(l.[Contract #]))
        """,
        """
        -- Manual Add
alter table [dbo].[Vizient Manual Add] add filename nvarchar(255)
        """,
        """
        update [dbo].[Vizient Manual Add] set filename = 'Vizient Manual Add' where filename is null
        """,
        """
        -- 36
delete from [dbo].[Vizient Manual Add] where [Contract Header] IN ('Contract Party','Contract Party Contact')
        """,
        """
        -- (2 rows affected) add all new fields needed
alter table [dbo].[Vizient Manual Add] add vizient_updated_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Vizient Manual Add] add replacement_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Vizient Manual Add] add final_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Vizient Manual Add] add  [Parties KP Legal Entity] nvarchar(255)
        """,
        """
        alter table [dbo].[Vizient Manual Add] add [Financial Commitment] nvarchar(255)
        """,
        """
        alter table [dbo].[Vizient Manual Add] add [Updated_Owner_Login] nvarchar(255)
        """,
        """
        alter table [dbo].[Vizient Manual Add] add [Updated_Business_User] nvarchar(255)
        """,
        """
        alter table [dbo].[Vizient Manual Add] add [Updated_Commodity_Name] nvarchar(255)
        """,
        """
        -- 1. Supplier Checks/Updates
update [dbo].[Vizient Manual Add] set vizient_updated_supplier=null
        """,
        """
        -- vizient updated supplier
update [dbo].[Vizient Manual Add] set vizient_updated_supplier=ltrim(rtrim(case when v.[Replacement]='' then v.[Search OL ID with Vizient TIN] else v.[Replacement] end)) from [dbo].[Vizient Manual Add] o inner join [dbo].[Task906129_final_Vizient_active_contracts_20240430] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- (4 rows affected)
update [dbo].[Vizient Manual Add] set vizient_updated_supplier='100008941' where vizient_updated_supplier='10008941'
        """,
        """
        -- (0 row affected) replacement
update [dbo].[Vizient Manual Add] set replacement_supplier=ltrim(rtrim(r.[Replacement ID])) from [dbo].[Vizient Manual Add] o inner join [dbo].[ReplacementVendors20240408] r on ltrim(rtrim(o.[Supplier Number]))=ltrim(rtrim(r.Vendor_Id))
        """,
        """
        -- (0 rows affected) final_supplier
update [dbo].[Vizient Manual Add] set final_supplier=case when replacement_supplier is null then [Supplier Number] else replacement_supplier end
        """,
        """
        -- (4 rows affected)
update [dbo].[Vizient Manual Add] set final_supplier=case isnull(vizient_updated_supplier,'') when '' then final_supplier else vizient_updated_supplier end
        """,
        """
        -- (4 rows affected)
select distinct final_supplier,vizient_updated_supplier,replacement_supplier,[Supplier Number] from [dbo].[Vizient Manual Add] --null, ''
        """,
        """
        -- check if in coupa
Select c.[Contract #],[Supplier Number] from [dbo].[Vizient Manual Add] c --inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where  not exists (Select 'X' from [dbo].[coupa_suppliers] s where c.final_supplier=s.[Supplier #] and s.status='active')
        """,
        """
        -- 14 2. update owner login, business user, Engagement Manager, published and execution date,[Offshore Service Addendum Required?] onwer login
update [dbo].[Vizient Manual Add] set [Updated_Owner_Login]= case [Owner Login] when 'D725503' then 'Y816499' when 'M044247' then 'A807108' when 'M582400' then 'Y245840' when 'Q444093' then 'T368292' when 'Y813310' then 'I263172' when 'Z758670' then	'B719287' when 'K726421' then 'F989776' else [Owner Login] end;
        """,
        """
        -- (674 rows affected) business user
update [dbo].[Vizient Manual Add] set [updated_business_user]=Updated_owner_login;
        """,
        """
        -- Engagement Manager
update [dbo].[Vizient Manual Add] set [Engagement Manager]='';
        """,
        """
        update [dbo].[Vizient Manual Add] set  [Offshore Service Addendum Required?]='No';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Default Account for Supplier Invoice]='';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Published Date]='',[Execution Date]='';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Financial Commitment]='No reportable financial commitment and/or contract term is under 1 year';
        """,
        """
        -- 4. update hierarchy type
update [dbo].[Vizient Manual Add] set [Hierarchy Type]='Contract'
        """,
        """
        -- where [Contract Type Name] IN ('VPA - Vizient Product Agreement','VSA - Vizient Standalone Agreement'); (674 rows affected)
select distinct [Hierarchy Type],[Contract Type Name] from [dbo].[Vizient Manual Add]
        """,
        """
        -- 5. update contract type custom fields
update [dbo].[Vizient Manual Add] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y';
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select * --distinct [Contract Type Custom Field 8] from [dbo].[Vizient Manual Add] where [Contract Type Custom Field 8]='';
        """,
        """
        -- ****there is a blank in 1 contract.. CHECK WITH MEENA Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [dbo].[Vizient Manual Add]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
select distinct [Contract Details Contract Type Custom Field 1] from [Vizient Manual Add] update [dbo].[Vizient Manual Add] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO';
        """,
        """
        -- Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [dbo].[Vizient Manual Add]
        """,
        """
        select [Parties KP Legal Entity] from [dbo].[Vizient Manual Add]
        """,
        """
        -- update legal entity from vizient file check if all contracts exist in ccl
update  [dbo].[Vizient Manual Add] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' where [Parties KP Legal Entity]='Vizient - KP Select, LLC'
        """,
        """
        -- 6. update commodity from Meena's file
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Vizient Manual Add] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[Commodity Name];
        """,
        """
        -- (536 rows affected)
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Vizient Manual Add] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[DESCR60] where [Updated_Commodity_Name] is null;
        """,
        """
        -- (118 rows affected) one off updates
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Bed, Stretcher and Patient Equipment"' where [Commodity Name]='10553-Bed  Stretcher and Patent Care';
        """,
        """
        -- (15 rows affected)
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment';
        """,
        """
        -- (0 rows affected)
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment - Patient Lifts"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment - Patient Lifts';
        """,
        """
        -- (0 rows affected)
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Heating, Ventilating and Air Conditioning - HVAC"' where [Updated_Commodity_Name]='Heating, Ventilating and Air Conditioning - HVAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Housekeeping Uniforms, Gowns and Linens"' where [Updated_Commodity_Name]='Housekeeping Uniforms, Gowns and Linens';
        """,
        """
        -- (0 rows affected)
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Move, Add, Change - MAC"' where [Updated_Commodity_Name]='Move, Add, Change - MAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Parking, Valet and Shuttle Services"' where [Updated_Commodity_Name]='Parking, Valet and Shuttle Services';
        """,
        """
        -- (0 rows affected)
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]=ltrim(rtrim([Updated_Commodity_Name]));
        """,
        """
        -- (674 rows affected)
update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Move, Add, Change - MAC"' where [Commodity Name]='10491-Move  Add  Change (MAC)';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Heating, Ventilating and Air Conditioning - HVAC"' where [Commodity Name]='10490-Heating  Ventilating and Air Conditioning (HVAC)';
        """,
        """
        update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='"Parking, Valet and Shuttle Services"' where [Commodity Name]='10502-Parking  Valet and Shuttle Services';
        """,
        """
        -- do not update yet
/**update [dbo].[Vizient Manual Add] set [Updated_Commodity_Name]='Medical Supplies' where [Commodity Name]='Wound Care Management'; **/
        """,
        """
        select *--,[Updated_Commodity_Name],[Commodity Name] from  [dbo].[Vizient Manual Add] where [Updated_Commodity_Name] is null;
        """,
        """
        select distinct count([Contract #]) from [dbo].[Vizient Manual Add] where [Contract #] like 'OL_%'
        """,
        """
        -- export script
select [Contract Header] ,[Contract Name] ,[Contract #] ,[Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[final_supplier] as [Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,[Updated_Owner_Login] as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,[Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,[Published Date] ,[Execution Date] ,[Department Name] ,[Contract Type Name] ,[Contract Type Custom Field 1] ,[Contract Type Custom Field 2] ,[Contract Type Custom Field 3] ,[Contract Type Custom Field 4] ,[Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,[Price & Payment Contract Type Custom Field 1] ,[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,[Updated_Business_User] as [Business User*] ,[Engagement Type] ,[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,updated_commodity_name as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,[Parties KP Legal Entity] ,[Financial Commitment] from [dbo].[Vizient Manual Add]
        """,
        """
        SELECT distinct [Parties KP Legal Entity] FROM [dbo].[Vizient Manual Add] WHERE [Parties KP Legal Entity]  like '%,%'
        """,
        """
        update [dbo].[Vizient Manual Add] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' WHERE [Parties KP Legal Entity] ='KP Select, LLC'
        """,
        """
        update [dbo].[Vizient Manual Add] set [Parties KP Legal Entity]='"Vizient - Vizient Supply, LLC"' WHERE [Parties KP Legal Entity] ='Vizient Supply, LLC'
        """,
        """
        -- T's
select* into [dbo].[Prod_T_2024-04-19_Load] from [dbo].[Prod_T_2024-04-19]
        """,
        """
        -- add all new fields needed
alter table [dbo].[Prod_T_2024-04-19_Load] add vizient_updated_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add replacement_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add final_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add final_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add  [Parties KP Legal Entity] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Financial Commitment] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Updated_Owner_Login] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Updated_Business_User] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Updated_Commodity_Name] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add Batch nvarchar(255)
        """,
        """
        -- 1. Supplier Checks/Updates
update [dbo].[Prod_T_2024-04-19_Load] set vizient_updated_supplier=null
        """,
        """
        -- vizient updated supplier
update [dbo].[Prod_T_2024-04-19_Load] set vizient_updated_supplier=ltrim(rtrim(case when v.[Replacement]='' then v.[Search OL ID with Vizient TIN] else v.[Replacement] end)) from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[Task906129_final_Vizient_active_contracts_20240430] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- (306 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set vizient_updated_supplier='100008941' where vizient_updated_supplier='10008941'
        """,
        """
        -- replacement
update [dbo].[Prod_T_2024-04-19_Load] set replacement_supplier=ltrim(rtrim(r.[Replacement ID])) from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[ReplacementVendors20240408] r on ltrim(rtrim(o.[Supplier Number]))=ltrim(rtrim(r.Vendor_Id))
        """,
        """
        -- (11 rows affected) final_supplier
update [dbo].[Prod_T_2024-04-19_Load] set final_supplier=case when replacement_supplier is null then [Supplier Number] else replacement_supplier end
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set final_supplier=case isnull(vizient_updated_supplier,'') when '' then final_supplier else vizient_updated_supplier end
        """,
        """
        select distinct final_supplier,vizient_updated_supplier,replacement_supplier,[Supplier Number] from [dbo].[Prod_T_2024-04-19_Load] --null, ''
        """,
        """
        -- check if in coupa
Select c.[Contract #],[Supplier Number] --, Batch from [dbo].[Prod_T_2024-04-19_Load] c --inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where  not exists (Select 'X' from [dbo].[coupa_suppliers] s where c.final_supplier=s.[Supplier #] and s.status='active')
        """,
        """
        -- 12 2. update owner login, business user, Engagement Manager, published and execution date,[Offshore Service Addendum Required?] onwer login
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Owner_Login]= case [Owner Login] when 'D725503' then 'Y816499' when 'M044247' then 'A807108' when 'M582400' then 'Y245840' when 'Q444093' then 'T368292' when 'Y813310' then 'I263172' when 'Z758670' then	'B719287' else [Owner Login] end
        """,
        """
        select distinct [Owner Login], [Business User*],updated_owner_login,updated_business_user from [dbo].[Prod_T_2024-04-19_Load] where [Contract #]='KP80301'
        """,
        """
        -- business user
update [dbo].[Prod_T_2024-04-19_Load] set [updated_business_user]=Updated_owner_login
        """,
        """
        -- Engagement Manager
update [dbo].[Prod_T_2024-04-19_Load] set [Engagement Manager]=''
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set  [Offshore Service Addendum Required?]='No'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Default Account for Supplier Invoice]=''
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Published Date]='',[Execution Date]=''
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Financial Commitment]='No reportable financial commitment and/or contract term is under 1 year'
        """,
        """
        -- 4. update hierarchy type
update [dbo].[Prod_T_2024-04-19_Load] set [Hierarchy Type]='Contract' where [Contract Type Name] IN ('VPA - Vizient Product Agreement','VSA - Vizient Standalone Agreement')
        """,
        """
        -- 5. update contract type custom fields
update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y'
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select * --distinct [Contract Type Custom Field 8] from [dbo].[Prod_T_2024-04-19_Load] where [Contract Type Custom Field 8]=''
        """,
        """
        -- ****there is a blank in 1 contract.. CHECK WITH MEENA Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
select distinct [Contract Details Contract Type Custom Field 1] from [Prod_T_2024-04-19_Load] update [dbo].[Prod_T_2024-04-19_Load] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO'
        """,
        """
        -- Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- update legal entity from vizient file check if all contracts exist in ccl
select * from [dbo].[Prod_T_2024-04-19_Load] o where not  exists (select 'X' from [dbo].[CCL-April2024-103328] v where ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))) and o.batch='Batch3'
        """,
        """
        select distinct left(o.[Contract #],2),v.[Contract Type] from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])) where batch='Batch3'
        """,
        """
        -- where left(o.[Contract #],2)='BM'
select distinct [Contract ID],[Contract Type] from [dbo].[CCL-April2024-103328]
        """,
        """
        update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- (303 rows affected) checked against MB missing file
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' where [Parties KP Legal Entity] is null
        """,
        """
        -- (21 rows affected) update batch
update  [dbo].[Prod_T_2024-04-19_Load] set batch= b.[Batch] from [Prod_T_2024-04-19_Load] o inner join [dbo].[Prod_T_VizientContractsMaster] b on o.[Contract #]=b.[Folder Name]
        """,
        """
        -- done till here 6. update commodity from Meena's file
select distinct [Commodity Name],updated_commodity_name
        """,
        """
        -- ,charindex('-',[Commodity Name]),SUBSTRING([Commodity Name],(charindex('-',[Commodity Name])+1),len([Commodity Name]))
from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        select distinct final_commodity_name from [dbo].[VizientCommodityMapping] where final_commodity_name like '%,%'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[Commodity Name]
        """,
        """
        -- 239
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[DESCR60] where [Updated_Commodity_Name] is null
        """,
        """
        -- 72 one off updates
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Bed, Stretcher and Patient Equipment"' where [Commodity Name]='10553-Bed  Stretcher and Patent Care'
        """,
        """
        -- (13 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment'
        """,
        """
        -- (13 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment - Patient Lifts"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment - Patient Lifts'
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Heating, Ventilating and Air Conditioning - HVAC"' where [Updated_Commodity_Name]='Heating, Ventilating and Air Conditioning - HVAC'
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Housekeeping Uniforms, Gowns and Linens"' where [Updated_Commodity_Name]='Housekeeping Uniforms, Gowns and Linens'
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Move, Add, Change - MAC"' where [Updated_Commodity_Name]='Move, Add, Change - MAC'
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Parking, Valet and Shuttle Services"' where [Updated_Commodity_Name]='Parking, Valet and Shuttle Services'
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]=ltrim(rtrim([Updated_Commodity_Name]))
        """,
        """
        select distinct [Updated_Commodity_Name],[Commodity Name] from  [dbo].[Prod_T_2024-04-19_Load] where [Updated_Commodity_Name] is null
        """,
        """
        -- export script
select [Contract Header] ,[Contract Name] ,[Contract #] ,[Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[final_supplier] as [Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,[Updated_Owner_Login] as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,[Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,[Published Date] ,[Execution Date] ,[Department Name] ,[Contract Type Name] ,[Contract Type Custom Field 1] ,[Contract Type Custom Field 2] ,[Contract Type Custom Field 3] ,[Contract Type Custom Field 4] ,[Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,[Price & Payment Contract Type Custom Field 1] ,[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,[Updated_Business_User] as [Business User*] ,[Engagement Type] ,[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,updated_commodity_name as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,[Parties KP Legal Entity] ,[Financial Commitment] from [dbo].[Prod_T_2024-04-19_Load] where batch='Batch1' and [Contract #] IN ('KP80804','KPMA149')
        """,
        """
        -- New T's
select* into [dbo].[Prod_T_2024-04-19_Load] from [dbo].[Prod_T_2024-04-19]
        """,
        """
        -- (324 rows affected)
alter table [dbo].[Prod_T_2024-04-19_Load] add filename nvarchar(255)
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set filename = 'T_2024-04-19' where filename is null
        """,
        """
        -- 36
select distinct filename from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- Prod Vizient Delta Process
alter table [dbo].[Prod_Vizient_Delta_T] add filename nvarchar(255)
        """,
        """
        delete from [dbo].[Prod_Vizient_Delta_T] where [Contract Header] IN ('Contract Party','Contract Party Contact')
        """,
        """
        -- (2 rows affected)
update [dbo].[Prod_Vizient_Delta_T] set filename = 'T_2024-05-06' where filename is null
        """,
        """
        -- (15 rows affected) find contracts that exists in orginal
select distinct [Contract #] into Prod_Vizient_Orig_Deltas_T from [dbo].[Prod_Vizient_Delta_T] d where  exists (Select 'X' from [dbo].[Prod_T_2024-04-19_Load] l where ltrim(rtrim(d.[Contract #]))=ltrim(rtrim(l.[Contract #])))
        """,
        """
        -- (13 row affected) delete delta contracts from original table
delete from [dbo].[Prod_T_2024-04-19_Load] where ltrim(rtrim([Contract #])) IN (Select distinct ltrim(rtrim([Contract #])) from Prod_Vizient_Orig_Deltas_T)
        """,
        """
        -- (13 row affected) add deltas into original table
insert into [dbo].[Prod_T_2024-04-19_Load] select * from [dbo].[Prod_Vizient_Delta_T] where ltrim(rtrim([Contract #])) IN (Select distinct ltrim(rtrim([Contract #])) from Prod_Vizient_Orig_Deltas_T)
        """,
        """
        -- (13 rows affected) add brand new contracts in deltas
insert into [dbo].[Prod_T_2024-04-19_Load] select * from [dbo].[Prod_Vizient_Delta_T] where ltrim(rtrim([Contract #])) IN ('KP82311','KP81754')
        """,
        """
        -- (2 rows affected) add all new fields needed
alter table [dbo].[Prod_T_2024-04-19_Load] add vizient_updated_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add replacement_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add final_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add  [Parties KP Legal Entity] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Financial Commitment] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Updated_Owner_Login] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Updated_Business_User] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Updated_Commodity_Name] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add Batch nvarchar(255)
        """,
        """
        -- 1. Supplier Checks/Updates
update [dbo].[Prod_T_2024-04-19_Load] set vizient_updated_supplier=null --326
        """,
        """
        -- vizient updated supplier
update [dbo].[Prod_T_2024-04-19_Load] set vizient_updated_supplier=ltrim(rtrim(case when v.[Replacement]='' then v.[Search OL ID with Vizient TIN] else v.[Replacement] end)) from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[Task906129_final_Vizient_active_contracts_20240430] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- (307 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set vizient_updated_supplier='100008941' where vizient_updated_supplier='10008941'
        """,
        """
        -- (0 row affected) replacement
update [dbo].[Prod_T_2024-04-19_Load] set replacement_supplier=ltrim(rtrim(r.[Replacement ID])) from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[ReplacementVendors20240408] r on ltrim(rtrim(o.[Supplier Number]))=ltrim(rtrim(r.Vendor_Id))
        """,
        """
        -- (11 rows affected) final_supplier
update [dbo].[Prod_T_2024-04-19_Load] set final_supplier=case when replacement_supplier is null then [Supplier Number] else replacement_supplier end
        """,
        """
        -- (326 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set final_supplier=case isnull(vizient_updated_supplier,'') when '' then final_supplier else vizient_updated_supplier end
        """,
        """
        -- (326 rows affected)
select distinct final_supplier,vizient_updated_supplier,replacement_supplier,[Supplier Number] from [dbo].[Prod_T_2024-04-19_Load] --null, ''
        """,
        """
        -- check if in coupa
Select c.[Contract #],[Supplier Number] , Batch from [dbo].[Prod_T_2024-04-19_Load] c --inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where  not exists (Select 'X' from [dbo].[coupa_suppliers] s where c.final_supplier=s.[Supplier #] and s.status='active')
        """,
        """
        -- 0 2. update owner login, business user, Engagement Manager, published and execution date,[Offshore Service Addendum Required?] onwer login
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Owner_Login]= case [Owner Login] when 'D725503' then 'Y816499' when 'M044247' then 'A807108' when 'M582400' then 'Y245840' when 'Q444093' then 'T368292' when 'Y813310' then 'I263172' when 'Z758670' then	'B719287' when 'K726421' then 'F989776' else [Owner Login] end;
        """,
        """
        -- (324 rows affected) business user
update [dbo].[Prod_T_2024-04-19_Load] set [updated_business_user]=Updated_owner_login;
        """,
        """
        -- Engagement Manager
update [dbo].[Prod_T_2024-04-19_Load] set [Engagement Manager]='';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set  [Offshore Service Addendum Required?]='No';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Default Account for Supplier Invoice]='';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Published Date]='',[Execution Date]='';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Financial Commitment]='No reportable financial commitment and/or contract term is under 1 year';
        """,
        """
        -- 4. update hierarchy type
update [dbo].[Prod_T_2024-04-19_Load] set [Hierarchy Type]='Contract' where [Contract Type Name] IN ('VPA - Vizient Product Agreement','VSA - Vizient Standalone Agreement');
        """,
        """
        -- (324 rows affected)
select distinct [Hierarchy Type],[Contract Type Name] from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- 5. update contract type custom fields
update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y';
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select * --distinct [Contract Type Custom Field 8] from [dbo].[Prod_T_2024-04-19_Load] where [Contract Type Custom Field 8]='';
        """,
        """
        -- ****there is a blank in 1 contract.. CHECK WITH MEENA Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
select distinct [Contract Details Contract Type Custom Field 1] from [Prod_T_2024-04-19_Load] update [dbo].[Prod_T_2024-04-19_Load] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO'; --69
        """,
        """
        -- Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- update legal entity from vizient file check if all contracts exist in ccl
select * from [dbo].[Prod_T_2024-04-19_Load] o where not  exists (select 'X' from [dbo].[CCL-April2024-103328] v where ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])))
        """,
        """
        -- 21
select distinct left(o.[Contract #],2),v.[Contract Type] --o.[Contract #],v.[Contract Type]-- from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- where left(o.[Contract #],2)='BM'
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - Vizient Supply, LLC"' from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])) where v.[Contract Type]='GPO'
        """,
        """
        -- (0 rows affected)
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])) where v.[Contract Type]='KPS'
        """,
        """
        -- (0 rows affected)
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])) where o.[Contract #] like 'KP%' and [Parties KP Legal Entity] is null
        """,
        """
        -- (293 rows affected)
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' where [Contract #] like 'KP%' and [Parties KP Legal Entity] is null
        """,
        """
        -- (20 rows affected)
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' where [Contract #] like 'BM%' and [Parties KP Legal Entity] is null
        """,
        """
        -- (10 rows affected)
select distinct [Contract #],left([Contract #],2) from [dbo].[Prod_T_2024-04-19_Load] where [Parties KP Legal Entity] is null
        """,
        """
        -- update with MB missing contract list
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]=v.[Legal Entity Type] from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[MB_Contracts Missing in April CCL] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract #])) where [Parties KP Legal Entity] is null
        """,
        """
        -- (1 rows affected)
select distinct left([Contract #],2),[Contract #] from [dbo].[Prod_T_2024-04-19_Load] where  [Parties KP Legal Entity] is null
        """,
        """
        -- checked against MB missing file
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' where [Parties KP Legal Entity] is null
        """,
        """
        -- (1 rows affected) 6. update commodity from Meena's file
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[Commodity Name];
        """,
        """
        -- (536 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[DESCR60] where [Updated_Commodity_Name] is null;
        """,
        """
        -- (118 rows affected) one off updates
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Bed, Stretcher and Patient Equipment"' where [Commodity Name]='10553-Bed  Stretcher and Patent Care';
        """,
        """
        -- (15 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment - Patient Lifts"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment - Patient Lifts';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Heating, Ventilating and Air Conditioning - HVAC"' where [Updated_Commodity_Name]='Heating, Ventilating and Air Conditioning - HVAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Housekeeping Uniforms, Gowns and Linens"' where [Updated_Commodity_Name]='Housekeeping Uniforms, Gowns and Linens';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Move, Add, Change - MAC"' where [Updated_Commodity_Name]='Move, Add, Change - MAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Parking, Valet and Shuttle Services"' where [Updated_Commodity_Name]='Parking, Valet and Shuttle Services';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]=ltrim(rtrim([Updated_Commodity_Name]));
        """,
        """
        -- (674 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Move, Add, Change - MAC"' where [Commodity Name]='10491-Move  Add  Change (MAC)';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Heating, Ventilating and Air Conditioning - HVAC"' where [Commodity Name]='10490-Heating  Ventilating and Air Conditioning (HVAC)';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Parking, Valet and Shuttle Services"' where [Commodity Name]='10502-Parking  Valet and Shuttle Services';
        """,
        """
        select distinct [Updated_Commodity_Name],[Commodity Name] from  [dbo].[Prod_T_2024-04-19_Load] where [Updated_Commodity_Name] is null;
        """,
        """
        -- update batch
update [dbo].[Prod_T_2024-04-19_Load] set Batch=m.Batch from [dbo].[Prod_T_2024-04-19_Load] l inner join [dbo].[Prod_T_VizientContractsMaster] m on ltrim(rtrim(m.[Folder Name]))=ltrim(rtrim(l.[Contract #]))
        """,
        """
        select distinct batch,count([Contract #]) from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- where [Contract #] like 'OL_%'
group by batch
        """,
        """
        -- export script
select [Contract Header] ,[Contract Name] ,[Contract #] ,[Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[final_supplier] as [Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,[Updated_Owner_Login] as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,[Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,[Published Date] ,[Execution Date] ,[Department Name] ,[Contract Type Name] ,[Contract Type Custom Field 1] ,[Contract Type Custom Field 2] ,[Contract Type Custom Field 3] ,[Contract Type Custom Field 4] ,[Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,[Price & Payment Contract Type Custom Field 1] ,[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,[Updated_Business_User] as [Business User*] ,[Engagement Type] ,[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,updated_commodity_name as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,[Parties KP Legal Entity] ,[Financial Commitment] from [dbo].[Prod_T_2024-04-19_Load] where Batch='Batch7' and [Contract #] IN ('KP82014')
        """,
        """
        SELECT distinct [Parties KP Legal Entity] FROM [dbo].[Prod_T_2024-04-19_Load] WHERE [Parties KP Legal Entity]  like '%,%'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' WHERE [Parties KP Legal Entity] ='KP Select, LLC'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - Vizient Supply, LLC"' WHERE [Parties KP Legal Entity] ='Vizient Supply, LLC'
        """,
        """
        -- U's
select* into [dbo].[Prod_T_2024-04-19_Load] from [dbo].[Prod_T_2024-04-19]
        """,
        """
        -- (666 rows affected)
alter table [dbo].[Prod_T_2024-04-19_Load] add filename nvarchar(255)
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set filename = 'U_2024-04-22' where filename is null
        """,
        """
        -- 36
select distinct filename from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- Prod Vizient Delta Process
alter table [dbo].[Prod_Vizient_Delta_U] add filename nvarchar(255)
        """,
        """
        delete from [dbo].[Prod_Vizient_Delta_U] where [Contract Header] IN ('Contract Party','Contract Party Contact')
        """,
        """
        -- (2 rows affected)
update [dbo].[Prod_Vizient_Delta_U] set filename = 'U_2024-05-06' where filename is null
        """,
        """
        -- (47 rows affected) find contracts that exists in orginal
select distinct [Contract #] into Prod_Vizient_Orig_Deltas_U from [dbo].[Prod_Vizient_Delta_U] d where  exists (Select 'X' from [dbo].[Prod_T_2024-04-19_Load] l where ltrim(rtrim(d.[Contract #]))=ltrim(rtrim(l.[Contract #])))
        """,
        """
        -- (39 row affected) delete delta contracts from original table
delete from [dbo].[Prod_T_2024-04-19_Load] where ltrim(rtrim([Contract #])) IN (Select distinct ltrim(rtrim([Contract #])) from Prod_Vizient_Orig_Deltas_U)
        """,
        """
        -- (39 row affected) add deltas into original table
insert into [dbo].[Prod_T_2024-04-19_Load] select * from [dbo].[Prod_Vizient_Delta_U]
        """,
        """
        -- where ltrim(rtrim([Contract #])) IN (Select distinct ltrim(rtrim([Contract #])) from Prod_Vizient_Orig_Deltas_X) (47 rows affected) add all new fields needed
alter table [dbo].[Prod_T_2024-04-19_Load] add vizient_updated_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add replacement_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add final_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add  [Parties KP Legal Entity] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Financial Commitment] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Updated_Owner_Login] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Updated_Business_User] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add [Updated_Commodity_Name] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_T_2024-04-19_Load] add Batch nvarchar(255)
        """,
        """
        -- 1. Supplier Checks/Updates
update [dbo].[Prod_T_2024-04-19_Load] set vizient_updated_supplier=null
        """,
        """
        -- vizient updated supplier
update [dbo].[Prod_T_2024-04-19_Load] set vizient_updated_supplier=ltrim(rtrim(case when v.[Replacement]='' then v.[Search OL ID with Vizient TIN] else v.[Replacement] end)) from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[Task906129_final_Vizient_active_contracts_20240430] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- (632 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set vizient_updated_supplier='100008941' where vizient_updated_supplier='10008941'
        """,
        """
        -- (1 row affected) replacement
update [dbo].[Prod_T_2024-04-19_Load] set replacement_supplier=ltrim(rtrim(r.[Replacement ID])) from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[ReplacementVendors20240408] r on ltrim(rtrim(o.[Supplier Number]))=ltrim(rtrim(r.Vendor_Id))
        """,
        """
        -- (35 rows affected) final_supplier
update [dbo].[Prod_T_2024-04-19_Load] set final_supplier=case when replacement_supplier is null then [Supplier Number] else replacement_supplier end
        """,
        """
        -- (674 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set final_supplier=case isnull(vizient_updated_supplier,'') when '' then final_supplier else vizient_updated_supplier end
        """,
        """
        -- (674 rows affected)
select distinct final_supplier,vizient_updated_supplier,replacement_supplier,[Supplier Number] from [dbo].[Prod_T_2024-04-19_Load] --null, ''
        """,
        """
        -- check if in coupa
Select c.[Contract #],[Supplier Number] , Batch from [dbo].[Prod_T_2024-04-19_Load] c --inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where  not exists (Select 'X' from [dbo].[coupa_suppliers] s where c.final_supplier=s.[Supplier #] and s.status='active')
        """,
        """
        -- 14 2. update owner login, business user, Engagement Manager, published and execution date,[Offshore Service Addendum Required?] onwer login
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Owner_Login]= case [Owner Login] when 'D725503' then 'Y816499' when 'M044247' then 'A807108' when 'M582400' then 'Y245840' when 'Q444093' then 'T368292' when 'Y813310' then 'I263172' when 'Z758670' then	'B719287' else [Owner Login] end;
        """,
        """
        -- (674 rows affected) business user
update [dbo].[Prod_T_2024-04-19_Load] set [updated_business_user]=Updated_owner_login;
        """,
        """
        -- Engagement Manager
update [dbo].[Prod_T_2024-04-19_Load] set [Engagement Manager]='';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set  [Offshore Service Addendum Required?]='No';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Default Account for Supplier Invoice]='';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Published Date]='',[Execution Date]='';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Financial Commitment]='No reportable financial commitment and/or contract term is under 1 year';
        """,
        """
        -- 4. update hierarchy type
update [dbo].[Prod_T_2024-04-19_Load] set [Hierarchy Type]='Contract' where [Contract Type Name] IN ('VPA - Vizient Product Agreement','VSA - Vizient Standalone Agreement');
        """,
        """
        -- (674 rows affected)
select distinct [Hierarchy Type],[Contract Type Name] from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- 5. update contract type custom fields
update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y';
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select * --distinct [Contract Type Custom Field 8] from [dbo].[Prod_T_2024-04-19_Load] where [Contract Type Custom Field 8]='';
        """,
        """
        -- ****there is a blank in 1 contract.. CHECK WITH MEENA Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
select distinct [Contract Details Contract Type Custom Field 1] from [Prod_T_2024-04-19_Load] update [dbo].[Prod_T_2024-04-19_Load] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO';
        """,
        """
        -- Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [dbo].[Prod_T_2024-04-19_Load]
        """,
        """
        -- update legal entity from vizient file check if all contracts exist in ccl
select * from [dbo].[Prod_T_2024-04-19_Load] o where not  exists (select 'X' from [dbo].[CCL-April2024-103328] v where ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])))
        """,
        """
        -- KP10799 "Vizient - KP Select, LLC"
select distinct left(o.[Contract #],2),v.[Contract Type] --o.[Contract #],v.[Contract Type]-- from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- where left(o.[Contract #],2)='BM'
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - Vizient Supply, LLC"' from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])) where v.[Contract Type]='GPO'
        """,
        """
        -- (109 rows affected)
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])) where v.[Contract Type]='KPS'
        """,
        """
        -- (439 rows affected)
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])) where o.[Contract #] like 'KP%' and [Parties KP Legal Entity] is null
        """,
        """
        -- (55 rows affected)
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' where o.[Contract #] like 'KP%' and [Parties KP Legal Entity] is null
        """,
        """
        -- (33 rows affected) update with MB missing contract list
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]=v.[Legal Entity Type] from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[MB_Contracts Missing in April CCL] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract #])) where [Parties KP Legal Entity] is null
        """,
        """
        -- (27 rows affected)
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - Vizient Supply, LLC"' where [Contract #] IN ('SV2031KP','XR0606KP')
        """,
        """
        -- (2 rows affected)
select distinct left([Contract #],2),[Contract #] from [dbo].[Prod_T_2024-04-19_Load] where  [Parties KP Legal Entity] is null
        """,
        """
        -- checked against MB missing file
update  [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' where [Parties KP Legal Entity] is null
        """,
        """
        -- (1 rows affected) 6. update commodity from Meena's file
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[Commodity Name];
        """,
        """
        -- (536 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_T_2024-04-19_Load] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[DESCR60] where [Updated_Commodity_Name] is null;
        """,
        """
        -- (118 rows affected) one off updates
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Bed, Stretcher and Patient Equipment"' where [Commodity Name]='10553-Bed  Stretcher and Patent Care';
        """,
        """
        -- (15 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment - Patient Lifts"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment - Patient Lifts';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Heating, Ventilating and Air Conditioning - HVAC"' where [Updated_Commodity_Name]='Heating, Ventilating and Air Conditioning - HVAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Housekeeping Uniforms, Gowns and Linens"' where [Updated_Commodity_Name]='Housekeeping Uniforms, Gowns and Linens';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Move, Add, Change - MAC"' where [Updated_Commodity_Name]='Move, Add, Change - MAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Parking, Valet and Shuttle Services"' where [Updated_Commodity_Name]='Parking, Valet and Shuttle Services';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]=ltrim(rtrim([Updated_Commodity_Name]));
        """,
        """
        -- (674 rows affected)
update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Move, Add, Change - MAC"' where [Commodity Name]='10491-Move  Add  Change (MAC)';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Heating, Ventilating and Air Conditioning - HVAC"' where [Commodity Name]='10490-Heating  Ventilating and Air Conditioning (HVAC)';
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Updated_Commodity_Name]='"Parking, Valet and Shuttle Services"' where [Commodity Name]='10502-Parking  Valet and Shuttle Services';
        """,
        """
        select distinct [Updated_Commodity_Name],[Commodity Name] from  [dbo].[Prod_T_2024-04-19_Load] where [Updated_Commodity_Name] is null;
        """,
        """
        -- update batch
update [dbo].[Prod_T_2024-04-19_Load] set Batch=m.Batch from [dbo].[Prod_T_2024-04-19_Load] l inner join [dbo].[Prod_U_VizientContractsMaster] m on ltrim(rtrim(m.[Folder Name]))=ltrim(rtrim(l.[Contract #]))
        """,
        """
        select distinct batch,count([Contract #]) from [dbo].[Prod_T_2024-04-19_Load] where [Contract #] like 'OL_%' group by batch
        """,
        """
        -- export script
select [Contract Header] ,[Contract Name] ,[Contract #] ,[Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[final_supplier] as [Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,[Updated_Owner_Login] as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,[Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,[Published Date] ,[Execution Date] ,[Department Name] ,[Contract Type Name] ,[Contract Type Custom Field 1] ,[Contract Type Custom Field 2] ,[Contract Type Custom Field 3] ,[Contract Type Custom Field 4] ,[Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,[Price & Payment Contract Type Custom Field 1] ,[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,[Updated_Business_User] as [Business User*] ,[Engagement Type] ,[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,updated_commodity_name as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,[Parties KP Legal Entity] ,[Financial Commitment] from [dbo].[Prod_U_2024-04-22_Load] where [Contract #] IN  ('KP11012','KP11341')
        """,
        """
        SELECT distinct [Parties KP Legal Entity] FROM [dbo].[Prod_T_2024-04-19_Load] WHERE [Parties KP Legal Entity]  like '%,%'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' WHERE [Parties KP Legal Entity] ='KP Select, LLC'
        """,
        """
        update [dbo].[Prod_T_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - Vizient Supply, LLC"' WHERE [Parties KP Legal Entity] ='Vizient Supply, LLC'
        """,
        """
        -- find contracts not loaded
select distinct [Contract #],[Contract Name],[Contract Type Name],[Supplier Number],final_supplier from [Prod_T_2024-04-19_Load] v where not exists (Select 'x' from coupa_contracts c where c.[Contract #]=v.[Contract #])
        """,
        """
        select distinct [Contract #],[Contract Name],[Contract Type Name],[Supplier Number],final_supplier from [Prod_U_2024-04-22_Load] v where not exists (Select 'x' from coupa_contracts c where c.[Contract #]=v.[Contract #])
        """,
        """
        select * from OL_Supplier_Master where VENDOR_ID IN ('100211080','100135024','100182653','100023918','100204523','100213902','100195882')
        """,
        """
        select * from COUPA_Suppliers where [Supplier #] IN ('100211080','100135024','100182653','100023918','100204523','100213902','100195882')
        """,
        """
        select * from coupa_contracts where [Contract #]='MAS1208KP'
        """,
        """
        select distinct [Supplier Number],final_supplier from [Prod_U_2024-04-22_Load] where [Contract #]='MS1208KP'
        """,
        """
        select * from COUPA_Suppliers where [Supplier #]='100139435'
        """,
        """
        -- X's
select* into [dbo].[Prod_X_2024-04-19_Load] from [dbo].[Prod_X_2024-04-19]
        """,
        """
        -- (37 rows affected)
alter table [dbo].[Prod_X_2024-04-19_Load] add filename nvarchar(255)
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set filename = 'X_2024-04-19' where filename is null
        """,
        """
        -- 36
select distinct filename from [dbo].[Prod_X_2024-04-19_Load]
        """,
        """
        -- Prod Vizient Delta Process
alter table [dbo].[Prod_Vizient_Delta_X] add filename nvarchar(255)
        """,
        """
        delete from [dbo].[Prod_Vizient_Delta_X] where [Contract Header] IN ('Contract Party','Contract Party Contact')
        """,
        """
        -- (2 rows affected)
update [dbo].[Prod_Vizient_Delta_X] set filename = 'X_2024-05-06' where filename is null
        """,
        """
        -- (2 rows affected) find contracts that exists in orginal
select distinct [Contract #] --into Prod_Vizient_Orig_Deltas_X from [dbo].[Prod_Vizient_Delta_X] d where  exists (Select 'X' from [dbo].[Prod_X_2024-04-19_Load] l where ltrim(rtrim(d.[Contract #]))=ltrim(rtrim(l.[Contract #])))
        """,
        """
        -- (1 row affected) KP81700 delete delta contracts from original table
delete from [dbo].[Prod_X_2024-04-19_Load] where ltrim(rtrim([Contract #])) IN (Select distinct ltrim(rtrim([Contract #])) from Prod_Vizient_Orig_Deltas_X)
        """,
        """
        -- (1 row affected) add deltas into original table
insert into [dbo].[Prod_X_2024-04-19_Load] select * from [dbo].[Prod_Vizient_Delta_X]
        """,
        """
        -- where ltrim(rtrim([Contract #])) IN (Select distinct ltrim(rtrim([Contract #])) from Prod_Vizient_Orig_Deltas_X) (2 rows affected) add all new fields needed
alter table [dbo].[Prod_X_2024-04-19_Load] add vizient_updated_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_X_2024-04-19_Load] add replacement_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_X_2024-04-19_Load] add final_supplier nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_X_2024-04-19_Load] add  [Parties KP Legal Entity] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_X_2024-04-19_Load] add [Financial Commitment] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_X_2024-04-19_Load] add [Updated_Owner_Login] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_X_2024-04-19_Load] add [Updated_Business_User] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_X_2024-04-19_Load] add [Updated_Commodity_Name] nvarchar(255)
        """,
        """
        alter table [dbo].[Prod_X_2024-04-19_Load] add Batch nvarchar(255)
        """,
        """
        -- 1. Supplier Checks/Updates
update [dbo].[Prod_X_2024-04-19_Load] set vizient_updated_supplier=null
        """,
        """
        -- vizient updated supplier
update [dbo].[Prod_X_2024-04-19_Load] set vizient_updated_supplier=ltrim(rtrim(case when v.[Replacement]='' then v.[Search OL ID with Vizient TIN] else v.[Replacement] end)) from [dbo].[Prod_X_2024-04-19_Load] o inner join [dbo].[Task906129_final_Vizient_active_contracts_20240430] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- (37 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set vizient_updated_supplier='100008941' where vizient_updated_supplier='10008941'
        """,
        """
        -- replacement
update [dbo].[Prod_X_2024-04-19_Load] set replacement_supplier=ltrim(rtrim(r.[Replacement ID])) from [dbo].[Prod_X_2024-04-19_Load] o inner join [dbo].[ReplacementVendors20240408] r on ltrim(rtrim(o.[Supplier Number]))=ltrim(rtrim(r.Vendor_Id))
        """,
        """
        -- (3 rows affected) final_supplier
update [dbo].[Prod_X_2024-04-19_Load] set final_supplier=case when replacement_supplier is null then [Supplier Number] else replacement_supplier end
        """,
        """
        -- (38 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set final_supplier=case isnull(vizient_updated_supplier,'') when '' then final_supplier else vizient_updated_supplier end
        """,
        """
        -- (38 rows affected)
select distinct final_supplier,vizient_updated_supplier,replacement_supplier,[Supplier Number] from [dbo].[Prod_X_2024-04-19_Load] --null, ''
        """,
        """
        -- check if in coupa
Select c.[Contract #],[Supplier Number] --, Batch from [dbo].[Prod_X_2024-04-19_Load] c --inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where  not exists (Select 'X' from [dbo].[coupa_suppliers] s where c.final_supplier=s.[Supplier #] and s.status='active')
        """,
        """
        -- 12 2. update owner login, business user, Engagement Manager, published and execution date,[Offshore Service Addendum Required?] onwer login
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Owner_Login]= case [Owner Login] when 'D725503' then 'Y816499' when 'M044247' then 'A807108' when 'M582400' then 'Y245840' when 'Q444093' then 'T368292' when 'Y813310' then 'I263172' when 'Z758670' then	'B719287' else [Owner Login] end;
        """,
        """
        -- (38 rows affected) business user
update [dbo].[Prod_X_2024-04-19_Load] set [updated_business_user]=Updated_owner_login;
        """,
        """
        -- (38 rows affected) Engagement Manager
update [dbo].[Prod_X_2024-04-19_Load] set [Engagement Manager]='';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set  [Offshore Service Addendum Required?]='No';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Default Account for Supplier Invoice]='';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Published Date]='',[Execution Date]='';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Financial Commitment]='No reportable financial commitment and/or contract term is under 1 year';
        """,
        """
        -- 4. update hierarchy type
update [dbo].[Prod_X_2024-04-19_Load] set [Hierarchy Type]='Contract' where [Contract Type Name] IN ('VPA - Vizient Product Agreement','VSA - Vizient Standalone Agreement');
        """,
        """
        -- (0 rows affected)
select distinct [Hierarchy Type],[Contract Type Name] from [dbo].[Prod_X_2024-04-19_Load]
        """,
        """
        -- 5. update contract type custom fields
update [dbo].[Prod_X_2024-04-19_Load] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N';
        """,
        """
        update [dbo].[Prod_X_2024-04-19_Load] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y';
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select * --distinct [Contract Type Custom Field 8] from [dbo].[Prod_X_2024-04-19_Load] where [Contract Type Custom Field 8]='';
        """,
        """
        -- ****there is a blank in 1 contract.. CHECK WITH MEENA Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [dbo].[Prod_X_2024-04-19_Load]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
select distinct [Contract Details Contract Type Custom Field 1] from [Prod_X_2024-04-19_Load] update [dbo].[Prod_X_2024-04-19_Load] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO';
        """,
        """
        -- Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [dbo].[Prod_X_2024-04-19_Load]
        """,
        """
        -- update legal entity from vizient file check if all contracts exist in ccl
select * from [dbo].[Prod_X_2024-04-19_Load] o where not  exists (select 'X' from [dbo].[CCL-April2024-103328] v where ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID])))
        """,
        """
        -- KP10799 "Vizient - KP Select, LLC"
select distinct left(o.[Contract #],2),v.[Contract Type] --o.[Contract #],v.[Contract Type]-- from [dbo].[Prod_X_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- where left(o.[Contract #],2)='BM'
update  [dbo].[Prod_X_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' from [dbo].[Prod_X_2024-04-19_Load] o inner join [dbo].[CCL-April2024-103328] v on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(v.[Contract ID]))
        """,
        """
        -- (37 rows affected) checked against MB missing file
update  [dbo].[Prod_X_2024-04-19_Load] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"' where [Parties KP Legal Entity] is null
        """,
        """
        -- (1 rows affected) 6. update commodity from Meena's file
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_X_2024-04-19_Load] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[Commodity Name];
        """,
        """
        -- (29 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]=c.final_commodity_name from [dbo].[Prod_X_2024-04-19_Load] o inner join [dbo].[VizientCommodityMapping] c on SUBSTRING(o.[Commodity Name],(charindex('-',o.[Commodity Name])+1),len(o.[Commodity Name]))=c.[DESCR60] where [Updated_Commodity_Name] is null;
        """,
        """
        -- (8 rows affected) one off updates
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]='"Bed, Stretcher and Patient Equipment"' where [Commodity Name]='10553-Bed  Stretcher and Patent Care';
        """,
        """
        -- (1 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]='"Furniture, Fixtures and Equipment - Patient Lifts"' where [Updated_Commodity_Name]='Furniture, Fixtures and Equipment - Patient Lifts';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]='"Heating, Ventilating and Air Conditioning - HVAC"' where [Updated_Commodity_Name]='Heating, Ventilating and Air Conditioning - HVAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]='"Housekeeping Uniforms, Gowns and Linens"' where [Updated_Commodity_Name]='Housekeeping Uniforms, Gowns and Linens';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]='"Move, Add, Change - MAC"' where [Updated_Commodity_Name]='Move, Add, Change - MAC';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]='"Parking, Valet and Shuttle Services"' where [Updated_Commodity_Name]='Parking, Valet and Shuttle Services';
        """,
        """
        -- (0 rows affected)
update [dbo].[Prod_X_2024-04-19_Load] set [Updated_Commodity_Name]=ltrim(rtrim([Updated_Commodity_Name]));
        """,
        """
        select distinct [Updated_Commodity_Name],[Commodity Name] from  [dbo].[Prod_X_2024-04-19_Load] where [Updated_Commodity_Name] is null;
        """,
        """
        -- export script
select [Contract Header] ,[Contract Name] ,[Contract #] ,[Hierarchy Type] ,[Parent Contract Number] ,[Parent Contract Name] ,[Supplier Name] ,[final_supplier] as [Supplier Number] ,[Starts] ,[Expires] ,[Status] ,[Legal Agreement] ,[Currency] ,[Source] ,[Supplier Account #] ,[Updated_Owner_Login] as [Owner Login] ,[Default On Unbacked Lines] ,[Supplier Can Invoice Directly] ,[Default Account Type for Supplier Invoice] ,[Default Account for Supplier Invoice] ,[Savings %] ,[Minimum Spend] ,[Maximum Spend] ,[Stop Spend Over Contract Value] ,[Content Groups] ,[Use Order Windows] ,[Payment Terms] ,[Shipping Terms] ,[Order Windows Sunday] ,[Order Windows Monday] ,[Order Windows Tuesday] ,[Order Windows Wednesday] ,[Order Windows Thursday] ,[Order Windows Friday] ,[Order Windows Saturday] ,[Order Windows Timezone] ,[Order Windows PO Message] ,[Order Windows Requisition Message] ,[Attachment 1] ,[Attachment 2] ,[Attachment 3] ,[Attachment 4] ,[Attachment 5] ,[Attachment 6] ,[Attachment 7] ,[Attachment 8] ,[Attachment 9] ,[Attachment 10] ,[Termination Notice] ,[Term Type] ,[Terminated] ,[Termination Reason Code] ,[Termination Reason Comment] ,[Consent to Assignment] ,[Used For Buying] ,[Automatically update expiry date] ,[No of Renewals] ,[Renewal Length(Unit)] ,[Renewal Length(Value)] ,[Length of Notice(Unit)] ,[Length of Notice(value)] ,[Termination Notice Length(Unit)] ,[Termination Notice Length(Value)] ,[Description] ,[Published Date] ,[Execution Date] ,[Department Name] ,[Contract Type Name] ,[Contract Type Custom Field 1] ,[Contract Type Custom Field 2] ,[Contract Type Custom Field 3] ,[Contract Type Custom Field 4] ,[Contract Type Custom Field 5] ,[Contract Type Custom Field 6] ,[Contract Type Custom Field 7] ,[Contract Type Custom Field 8] ,[Contract Type Custom Field 9] ,[Contract Type Custom Field 10] ,[Strict Invoicing Rules] ,[E-Signature Account] ,[External Contract Identifier] ,[Contract Classification] ,[Whose Paper] ,[Alternate Dispute Resolution] ,[Governing Law Country Region Code] ,[Jurisdiction Country Region Code] ,[Governing Law State] ,[Jurisdiction State] ,[Jurisdiction Exclusivity] ,[Nondisclosure Copying Restriction] ,[Permitted Disclosees Directors] ,[Permitted Disclosees Employees] ,[Permitted Disclosees Advisers] ,[Permitted Disclosees Contractors] ,[Notice Methods] ,[Contract Details Contract Type Custom Field 1] ,[Contract Details Contract Type Custom Field 2] ,[Contract Details Contract Type Custom Field 3] ,[Contract Details Contract Type Custom Field 4] ,[Contract Details Contract Type Custom Field 5] ,[Parties Contract Type Custom Field 1] ,[Parties Contract Type Custom Field 2] ,[Parties Contract Type Custom Field 3] ,[Parties Contract Type Custom Field 4] ,[Parties Contract Type Custom Field 5] ,[Term & Renewal Contract Type Custom Field 1] ,[Term & Renewal Contract Type Custom Field 2] ,[Term & Renewal Contract Type Custom Field 3] ,[Term & Renewal Contract Type Custom Field 4] ,[Term & Renewal Contract Type Custom Field 5] ,[Termination Contract Type Custom Field 1] ,[Termination Contract Type Custom Field 2] ,[Termination Contract Type Custom Field 3] ,[Termination Contract Type Custom Field 4] ,[Termination Contract Type Custom Field 5] ,[Performance Contract Type Custom Field 1] ,[Performance Contract Type Custom Field 2] ,[Performance Contract Type Custom Field 3] ,[Performance Contract Type Custom Field 4] ,[Performance Contract Type Custom Field 5] ,[Price & Payment Contract Type Custom Field 1] ,[Price & Payment Contract Type Custom Field 2] ,[Price & Payment Contract Type Custom Field 3] ,[Price & Payment Contract Type Custom Field 4] ,[Price & Payment Contract Type Custom Field 5] ,[Dispute & Remedies Contract Type Custom Field 1] ,[Dispute & Remedies Contract Type Custom Field 2] ,[Dispute & Remedies Contract Type Custom Field 3] ,[Dispute & Remedies Contract Type Custom Field 4] ,[Dispute & Remedies Contract Type Custom Field 5] ,[Risk Contract Type Custom Field 1] ,[Risk Contract Type Custom Field 2] ,[Risk Contract Type Custom Field 3] ,[Risk Contract Type Custom Field 4] ,[Risk Contract Type Custom Field 5] ,[IP & Data Contract Type Custom Field 1] ,[IP & Data Contract Type Custom Field 2] ,[IP & Data Contract Type Custom Field 3] ,[IP & Data Contract Type Custom Field 4] ,[IP & Data Contract Type Custom Field 5] ,[Relationship & Reporting Contract Type Custom Field 1] ,[Relationship & Reporting Contract Type Custom Field 2] ,[Relationship & Reporting Contract Type Custom Field 3] ,[Relationship & Reporting Contract Type Custom Field 4] ,[Relationship & Reporting Contract Type Custom Field 5] ,[Updated_Business_User] as [Business User*] ,[Engagement Type] ,[Engagement Manager] ,[Region Code Service Area] ,[Offshore Service Addendum Required?] ,[Countries of Operation] ,updated_commodity_name as [Commodity Name] ,[Parties Line of Business] ,[Parties Other LOB] ,[Price & Payment Estimated Spend] ,[Price & Payment Early Payment Discount Terms] ,[Price & Payment Rebates] ,[Parties KP Legal Entity] ,[Financial Commitment] from [dbo].[Prod_X_2024-04-19_Load]
        """,
        """
        delete from [dbo].[Prod_X_2024-04-19] where [Contract #] IN ('Contract Party Name','Entity Name')
        """,
        """
        -- check against ccl for Legal entity
select distinct u.[Contract #],u.[Contract Type Name] from [dbo].[Prod_U_2024-04-22] u where not exists (select 'X' from  [dbo].[CCL-April2024-103328] c where u.[Contract #]=c.[Contract ID])
        """,
        """
        select distinct u.[Contract #],u.[Contract Type Name] from [dbo].[Prod_T_2024-04-19] u where not exists (select 'X' from  [dbo].[CCL-April2024-103328] c where u.[Contract #]=c.[Contract ID])
        """,
        """
        select distinct u.[Contract #],u.[Contract Type Name] from [dbo].[Prod_X_2024-04-19] u where not exists (select 'X' from  [dbo].[CCL-April2024-103328] c where u.[Contract #]=c.[Contract ID])
        """,
        """
        select distinct u.[Contract #],c.[Contract Type] from [dbo].[Prod_U_2024-04-22] u inner join [dbo].[CCL-April2024-103328] c on u.[Contract #]=c.[Contract ID] where c.[Contract Type]='GPO' and c.[Contract ID] like 'KP%'-- IN ('KPR','PA')
        """,
        """
        select distinct u.[Contract #],c.[Contract Type] from [dbo].[Prod_X_2024-04-19] u inner join [dbo].[CCL-April2024-103328] c on u.[Contract #]=c.[Contract ID] where c.[Contract Type]='GPO' and c.[Contract ID] like 'KP%'--c.[Contract Type] IN ('KPR','PA')
        """,
        """
        select distinct u.[Contract #],c.[Contract Type] from [dbo].[Prod_T_2024-04-19] u inner join [dbo].[CCL-April2024-103328] c on c.[Contract Type]='GPO' and c.[Contract ID] like 'KP%'--u.[Contract #]=c.[Contract ID] where c.[Contract Type] IN ('KPR','PA')
        """,
        """
        -- commodity mapping checks
select * from [dbo].[VizientCommodityMapping]
        """,
        """
        select distinct [Commodity Name], from [dbo].[Prod_T_2024-04-19]
        """,
        """
        -- owner login work
select distinct [Contract #],[Owner Login] from [dbo].[Prod_T_2024-04-19] union select distinct [Contract #],[Owner Login] from [dbo].[Prod_X_2024-04-19] union select distinct [Contract #],[Owner Login] from [dbo].[Prod_U_2024-04-22]
        """,
        """
        -- old
select * from [dbo].[U_2024-03-22] v where exists (Select 'X' from [dbo].[VizientMasterDocument] m where m.[Folder Name]=v.[Contract #])
        """,
        """
        -- Subset of U for UAT -- Batch 1 and Batch 2
truncate table  [dbo].[UAT_U_2024-03-22]
        """,
        """
        insert into [dbo].[UAT_U_2024-03-22] select * from [dbo].[U_2024-03-22] v where exists (Select 'X' from [dbo].[VizientMasterDocument] m where m.[Folder Name]=v.[Contract #] and m.Batch IN ('Batch1','Batch2','Batch17'))
        """,
        """
        -- Contracts Meena needs
select * from [VizientMasterDocument] where [Folder Name] IN ('MS1168KP','KP81501')
        """,
        """
        -- 1. Supplier Checks
Select c.[Contract #],[Supplier Number] , Batch from [UAT_U_2024-03-22] c inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where not exists (Select 'X' from [dbo].[coupa_uat_suppliers] s where c.[Supplier Number]=s.[Supplier #] and s.status='active')
        """,
        """
        /** Contract #	Supplier Number	Batch BM14596	   100014428	Batch1 BM16360	   100018114	Batch1 BM18005	   100014428	Batch1 BM18037	   100150633	Batch2 CE2940KP   100058668	Batch2 LB0818	   100043126	Batch17 MS4530KP   100013127	Batch17 **/
        """,
        """
        -- 2. update owner login, business user, Engagement Manager, published and execution date,[Offshore Service Addendum Required?],
update [dbo].[UAT_U_2024-03-22] set [Owner Login]='T754533' ,[Business User*]='P529206' ,[Engagement Manager]='' ,[Offshore Service Addendum Required?]='No' ,[Default Account for Supplier Invoice]=''
        """,
        """
        -- (107 rows affected)
update [dbo].[UAT_U_2024-03-22] set [Published Date]='' ,[Execution Date]=''
        """,
        """
        -- (107 rows affected) add 2 new fields in the end
alter table [dbo].[UAT_U_2024-03-22] alter column  [Parties KP Legal Entity] nvarchar(255)
        """,
        """
        alter table [dbo].[UAT_U_2024-03-22] alter column [Financial Commitment] nvarchar(255)
        """,
        """
        -- 3. update the 2 new fields
update [dbo].[UAT_U_2024-03-22] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"'
        """,
        """
        -- (107 rows affected)
update [dbo].[UAT_U_2024-03-22] set [Financial Commitment]='No reportable financial commitment and/or contract term is under 1 year'
        """,
        """
        -- (107 rows affected) 4. update hierarchy type
update [dbo].[UAT_U_2024-03-22] set [Hierarchy Type]='Contract' where [Contract Type Name]='VSA - Vizient Standalone Agreement'
        """,
        """
        -- (107 rows affected) 5. update contract type custom fields
update [dbo].[UAT_U_2024-03-22] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N'
        """,
        """
        update [dbo].[UAT_U_2024-03-22] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y'
        """,
        """
        update [dbo].[UAT_U_2024-03-22] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N'
        """,
        """
        update [dbo].[UAT_U_2024-03-22] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y'
        """,
        """
        update [dbo].[UAT_U_2024-03-22] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N'
        """,
        """
        update [dbo].[UAT_U_2024-03-22] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y'
        """,
        """
        update [dbo].[UAT_U_2024-03-22] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N'
        """,
        """
        update [dbo].[UAT_U_2024-03-22] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y'
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select distinct [Contract Type Custom Field 8] from [UAT_U_2024-03-22]
        """,
        """
        -- Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [UAT_U_2024-03-22]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
select distinct [Contract Details Contract Type Custom Field 1] from [UAT_U_2024-03-22] update [UAT_U_2024-03-22] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO'
        """,
        """
        -- Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [UAT_U_2024-03-22]
        """,
        """
        -- 6. for UAT make all commodity blank
update [UAT_U_2024-03-22] set [Commodity Name]=''
        """,
        """
        -- Sanity check before export into comma delimted csv
Select distinct [Contract Type Name],[Hierarchy Type] from [dbo].[UAT_U_2024-03-22] -- VSA - Vizient Standalone Agreement	Master
        """,
        """
        -- first try with Meena's two contracts (found just one in U)
select * from [dbo].[UAT_U_2024-03-22] where [Contract #] IN ('MS1168KP','KP81501')
        """,
        """
        -- 2nd on export couple batches from U T's
select * into [dbo].[UAT_T_2024-03-22] from [dbo].[T_2024-03-22]
        """,
        """
        -- (316 rows affected) 1. Supplie Checks
Select c.[Contract #],[Supplier Number] --, Batch from [UAT_T_2024-03-22] c --inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where  not exists (Select 'X' from [dbo].[coupa_uat_suppliers] s where c.[Supplier Number]=s.[Supplier #] and s.status='active')
        """,
        """
        -- 12 2. update owner login, business user, Engagement Manager, published and execution date,[Offshore Service Addendum Required?]
update [dbo].[UAT_T_2024-03-22] set [Owner Login]='T754533' ,[Business User*]='P529206' ,[Engagement Manager]='' ,[Offshore Service Addendum Required?]='No' ,[Default Account for Supplier Invoice]=''
        """,
        """
        -- (316 rows affected)
update [dbo].[UAT_T_2024-03-22] set [Published Date]='' ,[Execution Date]=''
        """,
        """
        -- (316 rows affected) add 2 new fields in the end
alter table [dbo].[UAT_T_2024-03-22] add   [Parties KP Legal Entity] nvarchar(255)
        """,
        """
        alter table [dbo].[UAT_T_2024-03-22] add  [Financial Commitment] nvarchar(255)
        """,
        """
        -- update the 2 new fields
update [dbo].[UAT_T_2024-03-22] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"'
        """,
        """
        -- (316 rows affected)
update [dbo].[UAT_T_2024-03-22] set [Financial Commitment]='No reportable financial commitment and/or contract term is under 1 year'
        """,
        """
        -- (316 rows affected) 4. update hierarchy type
select distinct [Contract Type Name],[Hierarchy Type] from [UAT_T_2024-03-22] update [dbo].[UAT_T_2024-03-22] set [Hierarchy Type]='Contract' where [Contract Type Name] IN ('VPA - Vizient Product Agreement','VSA - Vizient Standalone Agreement')
        """,
        """
        -- (1 rows affected) 5. update contract type custom fields
update [dbo].[UAT_T_2024-03-22] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N'
        """,
        """
        update [dbo].[UAT_T_2024-03-22] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y'
        """,
        """
        update [dbo].[UAT_T_2024-03-22] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N'
        """,
        """
        update [dbo].[UAT_T_2024-03-22] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y'
        """,
        """
        update [dbo].[UAT_T_2024-03-22] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N'
        """,
        """
        update [dbo].[UAT_T_2024-03-22] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y'
        """,
        """
        update [dbo].[UAT_T_2024-03-22] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N'
        """,
        """
        update [dbo].[UAT_T_2024-03-22] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y'
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select distinct [Contract Type Custom Field 8] from [UAT_T_2024-03-22]
        """,
        """
        -- Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [UAT_T_2024-03-22]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
select distinct [Contract Details Contract Type Custom Field 1] from [UAT_T_2024-03-22] update [UAT_T_2024-03-22] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO'
        """,
        """
        -- Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [UAT_T_2024-03-22]
        """,
        """
        -- 6. for UAT make all commodity blank
update [UAT_T_2024-03-22] set [Commodity Name]=''
        """,
        """
        -- (1 row affected) X's
select * into [UAT_X_2024-03-22] from [dbo].[X_2024-03-22]
        """,
        """
        -- (39 rows affected) 1. Supplier Checks
Select c.[Contract #],[Supplier Number] from [UAT_X_2024-03-22] c --inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where not exists (Select 'X' from [dbo].[coupa_uat_suppliers] s where c.[Supplier Number]=s.[Supplier #] and s.status='active') /** Contract #	Supplier Number BM18075	100014428 KP82600	100030807 KP82700	100036142 **/
        """,
        """
        -- 2. update owner login, business user, Engagement Manager, published and execution date,[Offshore Service Addendum Required?]
update [dbo].[UAT_X_2024-03-22] set [Owner Login]='T754533' ,[Business User*]='P529206' ,[Engagement Manager]='' ,[Offshore Service Addendum Required?]='No' ,[Default Account for Supplier Invoice]=''
        """,
        """
        -- (39 rows affected)
update [dbo].[UAT_X_2024-03-22] set [Published Date]='' ,[Execution Date]=''
        """,
        """
        -- (39 rows affected) add 2 new fields in the end
alter table [dbo].[UAT_X_2024-03-22] add  [Parties KP Legal Entity] nvarchar(255)
        """,
        """
        alter table [dbo].[UAT_X_2024-03-22] add  [Financial Commitment] nvarchar(255)
        """,
        """
        -- 3. update the 2 new fields
update [dbo].[UAT_X_2024-03-22] set [Parties KP Legal Entity]='"Vizient - KP Select, LLC"'
        """,
        """
        -- (39 rows affected)
update [dbo].[UAT_X_2024-03-22] set [Financial Commitment]='No reportable financial commitment and/or contract term is under 1 year'
        """,
        """
        -- (39 rows affected) 4. update hierarchy type
select distinct [Hierarchy Type],[Contract Type Name] from [UAT_X_2024-03-22]
        """,
        """
        -- 5. update contract type custom fields
update [dbo].[UAT_X_2024-03-22] set [Contract Type Custom Field 1]='No' where [Contract Type Custom Field 1]='N'
        """,
        """
        update [dbo].[UAT_X_2024-03-22] set [Contract Type Custom Field 1]='Yes' where [Contract Type Custom Field 1]='Y'
        """,
        """
        update [dbo].[UAT_X_2024-03-22] set [Contract Type Custom Field 2]='No' where [Contract Type Custom Field 2]='N'
        """,
        """
        update [dbo].[UAT_X_2024-03-22] set [Contract Type Custom Field 2]='Yes' where [Contract Type Custom Field 2]='Y'
        """,
        """
        update [dbo].[UAT_X_2024-03-22] set [Contract Type Custom Field 4]='No' where [Contract Type Custom Field 4]='N'
        """,
        """
        update [dbo].[UAT_X_2024-03-22] set [Contract Type Custom Field 4]='Yes' where [Contract Type Custom Field 4]='Y'
        """,
        """
        update [dbo].[UAT_X_2024-03-22] set [Contract Type Custom Field 5]='No' where [Contract Type Custom Field 5]='N'
        """,
        """
        update [dbo].[UAT_X_2024-03-22] set [Contract Type Custom Field 5]='Yes' where [Contract Type Custom Field 5]='Y'
        """,
        """
        -- Contract Type Custom Field 8 -- only NPC or NSCLT
select distinct [Contract Type Custom Field 8] from [UAT_X_2024-03-22]
        """,
        """
        -- Contract Type Custom Field 9 -- only blank or date
select distinct [Contract Type Custom Field 9] from [UAT_X_2024-03-22]
        """,
        """
        -- Contract Details Contract Type Custom Field 1 (No./ Single/Multi/Dual/Blank)
select distinct [Contract Details Contract Type Custom Field 1] from [UAT_X_2024-03-22] update [UAT_X_2024-03-22] set [Contract Details Contract Type Custom Field 1]='No' where [Contract Details Contract Type Custom Field 1]='NO'
        """,
        """
        -- (32 rows affected) Price and Payment: Custom field 1  = Increase / Savings/ Neutral (if blank then Neutral)
select distinct [Price & Payment Contract Type Custom Field 1] from [UAT_X_2024-03-22]
        """,
        """
        -- 6. for UAT make all commodity blank
update [UAT_X_2024-03-22] set [Commodity Name]=''
        """,
        """
        -- X export
select * from [UAT_X_2024-03-22] where [Supplier Number] IN (Select [Supplier Number] from [UAT_X_2024-03-22] c --inner join [VizientMasterDocument] m on c.[Contract #]=m.[Folder Name] where  not exists (Select 'X' from [dbo].[coupa_uat_suppliers] s where c.[Supplier Number]=s.[Supplier #] and s.status='active'))
        """,
        """
        -- U export Batch1
select u.* from [UAT_U_2024-03-22] u inner join [VizientMasterDocument] m on u.[Contract #]=m.[Folder Name] where [Supplier Number] IN (Select [Supplier Number] from [UAT_U_2024-03-22] c where  exists (Select 'X' from [dbo].[coupa_uat_suppliers] s where c.[Supplier Number]=s.[Supplier #] and s.status='active')) and m.Batch = 'Batch1'
        """,
        """
        -- 36 U from Batch1 Batch2
select u.* from [UAT_U_2024-03-22] u inner join [VizientMasterDocument] m on u.[Contract #]=m.[Folder Name] where [Supplier Number] IN (Select [Supplier Number] from [UAT_U_2024-03-22] c where not exists (Select 'X' from [dbo].[coupa_uat_suppliers] s where c.[Supplier Number]=s.[Supplier #] and s.status='active')) and m.Batch = 'Batch2'
        """,
        """
        -- 31 U from Batch1 T Export
select t.* from [UAT_T_2024-03-22] t inner join [VizientMasterDocument] m on t.[Contract #]=m.[Folder Name] where [Supplier Number] IN (Select [Supplier Number] from [UAT_T_2024-03-22] c where  exists (Select 'X' from [dbo].[coupa_uat_suppliers] s where c.[Supplier Number]=s.[Supplier #] and s.status='active')) and m.Batch = 'Batch2' and m.[Parent Folder Name] = 'T_2024-03-22'
        """,
        """
        -- 60 T from Batch2
select * from [UAT_U_2024-03-22] where [Contract #] IN ('CE7408KP','BM16165','BM18019')
        """,
        """
        select u.* from [dbo].[UAT_U_2024-03-22] u inner join [VizientMasterDocument] m on u.[Contract #]=m.[Folder Name] where [Supplier Number] IN (Select [Supplier Number] from [UAT_U_2024-03-22] c where  exists (Select 'X' from [dbo].[coupa_uat_suppliers] s where c.[Supplier Number]=s.[Supplier #] and s.status='active')) and m.Batch IN ('Batch1', 'Batch2') union select * from [dbo].[UAT_X_2024-03-22] union select t.* from [dbo].[UAT_T_2024-03-22] t inner join [VizientMasterDocument] m on t.[Contract #]=m.[Folder Name] where [Supplier Number] IN (Select [Supplier Number] from [UAT_T_2024-03-22] c where  exists (Select 'X' from [dbo].[coupa_uat_suppliers] s where c.[Supplier Number]=s.[Supplier #] and s.status='active')) and m.Batch = 'Batch2' and m.[Parent Folder Name] = 'T_2024-03-22'
        """,
        """
        select distinct [Supplier ID ] from [dbo].[FSSBuyingChannels_HostedCatalogs]
        """,
        """
        select * from coupa_contracts
        """,
        """
        select r.*,c.[Contract #],c.[Contract Name],c.[Contract Type Name],c.Starts,c.Expires, c.Description,c.[Commodity Name] from [dbo].[FSSBuyingChannels_HostedCatalogs] r left join coupa_contracts c on ltrim(rtrim(r.[Supplier ID ]))=ltrim(rtrim(c.[Supplier Number])) order by ltrim(rtrim(r.[Supplier ID ])),c.[Contract Type Name]
        """,
        """
        select * from coupa_contracts where [Supplier Name] like '%emc%'
        """,
        """
        -- R2R Wave 2 Report Suppliers in R2R Wave2 in COUPA and their status
Select r.[Supplier ID],r.[Supplier Name],c.[Supplier #] as COUPA_Supplier#,c.[Name] as COUPA_Supplier_Name,c.[Status] as COUPA_Supplier_Status from [dbo].[COUPA_Suppliers] c right join [dbo].[R2R_Hosted_Catalog_Suppliers_Wave2] r on  c.[Supplier #] = r.[Supplier ID]
        """,
        """
        -- Active contracts in COUPA for R2R Wave2 suppliers - Hosted Catalog
Select distinct r.[Supplier ID],r.[Supplier Name],c.[Contract Type Name],c.[Contract #],c.[Hierarchy Type],c.Starts,c.Expires from [dbo].[coupa_contracts] c right join [dbo].[R2R_Hosted_Catalog_Suppliers_Wave2] r on  c.[Supplier Number] = r.[Supplier ID]
        """,
        """
        -- where Expires='' or cast(Expires as date)>'2024-04-30'
order by 1,2,3
        """,
        """
        -- Contracts for R2R vendors along with OL and COUPA Vendor Status
Select a.[Supplier ID],a.[Supplier Name],a.[Go Live Wave],a.COUPA_Status,a.OL_Status ,c.[Contract #],c.[Contract Name],c.[Contract Type Name],c.Description,c.[Commodity Name],c.Starts,c.Expires from (Select distinct r.[Supplier ID],r.[Supplier Name],r.[Go Live Wave],s.status as COUPA_Status,[VENDOR_STATUS] as OL_Status from [dbo].[R2R_Hosted_Catalog_Vendors_Updated052024] r left join [dbo].[COUPA_Suppliers] s on r.[Supplier ID]=s.[Supplier #] left join [dbo].[OL_R2R Hosted categog vendor] o on r.[Supplier ID]=o.[VENDOR_ID] ) a left join [dbo].[coupa_contracts] c on a.[Supplier ID]=c.[Supplier Number] order by [Supplier ID], [Contract Type Name]
        """,
        """
        select * from [dbo].[OneLink_Master_New] where [Supplier Number] IN ('100020742','100109810','100120263','100163997','100195296')
        """,
        """
        select * from [dbo].[OneLink_Master_Delta_Full] where [Supplier Number] IN ('100020742','100109810','100120263','100163997','100195296')
        """,
        """
        select distinct o.[Contract #] from [dbo].[Recon_OneLink_Master_New_Union] o left join coupa_contracts c on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(c.[Contract #])) where o.[Contract Type Name] ='Services Agreement' and c.[Contract #] is null
        """,
        """
        -- Recon report error numbers (non CAH)
Select distinct [Elevate Comments, if not delivered], count(distinct o.[Contract #]) from [dbo].[Recon_OneLink_Master_New_Union] o inner join [dbo].[Elevate Migration Tracker 05032024] e on ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(e.[Contract #])) where o.[Contract Type Name]='BAA - Business Associate Agreement' group by [Elevate Comments, if not delivered]
        """,
        """
        -- Recon report error numbers ( CAH)
Select distinct [Elevate Comments, if not delivered], count(distinct o.[Contract #]) from [dbo].[Recon_OneLink_Master_New_Union] o inner join [dbo].[Elevate Migration Tracker 05032024] e on ltrim(rtrim(replace(replace(o.[Contract #],'OL','CAH'),'HIC',''))) = e.[Contract #] where o.[Contract Type Name]='PPA - Participant Plan Agreement' group by [Elevate Comments, if not delivered]
        """,
        """
        -- contracts in coupa not in OL union
Select  o.* from  [dbo].[Recon_OneLink_Master_New_Union] o where not exists (Select 'X' from coupa_contracts c where ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(c.[Contract #]))) and  o.[Contract Type Name] ='BAA - Business Associate Agreement' --and o.[Supplier Number]=''
        """,
        """
        -- 458
Select  o.* from  [dbo].[Recon_OneLink_Master_New_Union] o where not exists (Select 'X' from coupa_contracts c where ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(c.[Contract #]))) and  o.[Contract Type Name] ='NDA - Mutual Non-Disclosure Agreement' and o.[Supplier Number]=''
        """,
        """
        -- 141 blank supp
Select  o.* from  [dbo].[Recon_OneLink_Master_New_Union] o where not exists (Select 'X' from coupa_contracts c where ltrim(rtrim(o.[Contract #]))=ltrim(rtrim(c.[Contract #]))) and  o.[Contract Type Name] ='LOA - Letter of Agreement' --and o.[Supplier Number]=''
        """,
        """
        -- Vizient supplier check truncate table Vizient_Missing_Supplier
select distinct  Replacement--[Vendor Name], [Search OL ID with Vizient TIN],[Replacement] from [dbo].[Task906129_final_Vizient_active_contracts_20240430] v
        """,
        """
        -- where [Search OL ID with Vizient TIN]='' add Judy's supplierNumber into [dbo].[Prod_Vizient_Full]
alter table [dbo].[Prod_Vizient_Full] add Final_Supplier_Number nvarchar(255)
        """,
        """
        update [dbo].[Prod_Vizient_Full] set Vizient_Supplier_Number=null,Final_Supplier_Number=null
        """,
        """
        update [dbo].[Prod_Vizient_Full] set Vizient_Supplier_Number=ltrim(rtrim(case when [Replacement]='' then [Search OL ID with Vizient TIN] else [Replacement] end)) from [dbo].[Prod_Vizient_Full] o inner join [dbo].[Task906129_final_Vizient_active_contracts_20240430] v on ltrim(rtrim(o.[Contract #]))=rtrim(ltrim(v.[Contract ID]))
        """,
        """
        -- 969
update [dbo].[Prod_Vizient_Full] set Vizient_Supplier_Number='100008941' where Vizient_Supplier_Number='10008941'
        """,
        """
        update [dbo].[Prod_Vizient_Full] set Final_Supplier_Number=null
        """,
        """
        update [dbo].[Prod_Vizient_Full] set Final_Supplier_Number=Vizient_Supplier_Number
        """,
        """
        update [dbo].[Prod_Vizient_Full] set Final_Supplier_Number=[Supplier Number] where Final_Supplier_Number is null
        """,
        """
        update [dbo].[Prod_Vizient_Full] set Final_Supplier_Number=[Supplier Number] where Final_Supplier_Number=''
        """,
        """
        select distinct Final_Supplier_Number, Vizient_Supplier_Number, [Supplier Number] from [dbo].[Prod_Vizient_Full] where [Supplier Number]='100008941'
        """,
        """
        truncate table Vizient_Missing_Supplier
        """,
        """
        -- find suppliers that do not exist in coupa
insert into Vizient_Missing_Supplier select distinct Final_Supplier_Number, 'Does Not Exist in COUPA' from [dbo].[Prod_Vizient_Full] v where not exists (Select 'X' from [dbo].[COUPA_Suppliers] c where ltrim(rtrim(v.Final_Supplier_Number))=ltrim(rtrim(c.[Supplier #])))
        """,
        """
        -- 13 find suppliers that is inactive in COUPA
insert into Vizient_Missing_Supplier select distinct  v.Final_Supplier_Number, 'Inactive' from [dbo].[Prod_Vizient_Full] v where  exists (Select 'X' from [dbo].[COUPA_Suppliers] c where ltrim(rtrim(v.Final_Supplier_Number))=ltrim(rtrim(c.[Supplier #])) and status='inactive')
        """,
        """
        -- 0 find suppliers that is inactive in COUPA
insert into Vizient_Missing_Supplier select distinct v.[Supplier Number] , 'Draft' from [dbo].[Prod_Vizient_Full] v where  exists (Select 'X' from [dbo].[COUPA_Suppliers] c where ltrim(rtrim(v.Final_Supplier_Number))=ltrim(rtrim(c.[Supplier #])) and status='draft')
        """,
        """
        -- 0
select * from Vizient_Missing_Supplier
        """,
        """
        -- run another check against replacement supplier table
select * from Vizient_Missing_Supplier v inner join [dbo].[ReplacementVendors20240408] r on ltrim(rtrim(v.[Supplier Number]))=ltrim(rtrim(r.[Vendor_Id]))
        """,
        """
        -- report to mdm team
Select distinct v.[Supplier Number], o.NAME1 as Supplier_Name,o.VENDOR_STATUS as OL_Vendor_Status,v.Reason as Coupa_Vendor_Status from Vizient_Missing_Supplier v left join [dbo].[OL_Supplier_Master] o on ltrim(rtrim(v.[Supplier Number]))=ltrim(rtrim(o.VENDOR_ID))
        """,
        """
        select * from [dbo].[ReplacementVendors20240408] where [Vendor_Id]='100008941' select * from COUPA_Suppliers where [Supplier #] IN ('100021598','100013992','100022086')
        """,
        """
        select * from [dbo].[OL_Supplier_Master] where [VENDOR_ID] IN ('100135024','100181426','100182653','100195882')
        """,
        """
        -- weekend invoice load for gl strings get unique gl string combinations
select distinct [Default Account for Supplier Invoice] from OneLink_Master_New union select distinct [Default Account for Supplier Invoice] from OneLink_Master_Delta_Full union select distinct [Default Account for Supplier Invoice] from OneLink_Master_New_FG union select distinct [Default Account for Supplier Invoice] from OneLink_Master_New_FG_delta
        """,
        """
        select * from [dbo].[GLString_GLUnitLocDept_UAT] where [External Ref Code] ='0201|20001|9920'
        """,
        """
        -- ('0101|30000|0279','0101|30000|7875','0201|20000|4030','0201|20001|9866','0201|20002|6265','0201|20002|9716','0201|21051|4490','0201|21051|4530','0201|21251|9716','0201|21863|4573','0206|20003|3604','0208|20000|3731','0208|20000|3731','0208|20000|6227','0208|20000|7087','0208|20000|7087','0208|20002|5968','0208|20002|6384','0208|20003|6264','0208|20003|6265','0208|20003|6265','0208|20003|6481','0208|20003|6484','0208|20003|6484','0208|20003|6889','0208|21251|4961','0308|30000|5968','0308|30000|7031','0308|30000|7059','0308|30000|7059','0308|30000|7305','0308|30000|7305','0308|30000|7305','0308|30000|7317','0308|30000|7326','0308|30000|7335','0308|30000|7339','0308|30000|7347','0308|30000|7348','0308|30000|7350','0308|30000|7351','0308|30000|7351','0308|30000|7352','0308|30000|7352','0308|30000|7354','0308|30000|7359','0308|30000|7359','0308|30000|7366','0308|30000|7366','0308|30000|7367','0308|30000|7375','0308|30000|7387','0308|30000|7395','0308|30000|7422','0308|30000|7422','0308|30000|7423','0308|30000|7430','0308|30000|7430','0308|30000|7430','0308|30000|7514','0308|30000|7533','0308|30000|7534','0308|30000|7539','0308|30000|7545','0308|30000|7555','0308|30000|7555','0308|30000|7555','0308|30000|7637','0308|30000|7657','0308|30000|7672','0308|30000|7714','0308|30000|7720','0308|30000|7732','0308|30000|7876','0308|30000|7879','0308|30000|7879','0308|30000|7880','0308|30000|7880','0308|30000|8208','0308|30000|9087','0308|30000|9200','0308|30000|9538','0315|16900|9050','0315|16991|9083','0315|16991|9083','0315|16991|9083','0315|20002|9085','0315|20002|9085','0315|20002|9085','0315|20002|9085','0315|20002|9085','0315|30000|7471','0315|30000|7477','0315|30000|7483','0315|30000|7484','0315|30000|7484','0315|30000|9007','0315|30000|9008','0315|30000|9047')
select * from GLString_List_UAT  --latest one Meena sent
        """,
        """
        select * from [dbo].[GLString_CleanUP Work 20241004]
        """,
        """
        -- get 100 gl strings that do not exist in UAT
Select distinct [Updated Default Account for Supplier Invoice] from [GLString_CleanUP Work 20241004] o where not exists (Select 'x' from GLString_List_UAT g where g.[Code]=o.[Updated Default Account for Supplier Invoice]) and load='yes'
        """,
        """
        -- 20 exists working invoice load
select * from [dbo].[InvLoad2] select * into [dbo].[GL String InvLoad2 orig 100 RiseNow] from [dbo].[GL String InvLoad2 orig 100]
        """,
        """
        select * from [dbo].[GL InvLoad2 orig 100 riseNow]
        """,
        """
        update [dbo].[GL String InvLoad2 orig 100 RiseNow] set [Supplier Name]='RiseNow',[Supplier Number]='100194930',[Remit To Address Street1]='',[Remit To Address City]='' ,[Remit To Address Postal Code]='',[Remit To Address Country Code]='',[Remit To Code]=''
        """,
        """
        select distinct [Default Account for Supplier Invoice] from OneLink_Master_New_FG o where exists (Select 'x' from GLString_List_UAT g where g.name=o.[Default Account for Supplier Invoice])
        """,
        """
        select distinct [Default Account for Supplier Invoice],left([Default Account for Supplier Invoice],len([Default Account for Supplier Invoice])) from OneLink_Master_New_FG
        """,
        """
        -- missing FG strings in UAT and Prod
select distinct * from [dbo].[FG_Contracts_GLCodes]
        """,
        """
        -- UAT checks GL
Select distinct [Cleansed Default Account for Supplier Invoice],[Segment1],[Segment2],[Segment3] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_GLUnitLocDept_UAT] u where f.Segment1=u.[External Ref Code])
        """,
        """
        Select distinct [Cleansed Default Account for Supplier Invoice],[Segment1],[Segment2],[Segment3] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_GLUnitLocDept_UAT] u where f.Segment1+'|'+f.Segment2=u.[External Ref Code])
        """,
        """
        Select distinct [Cleansed Default Account for Supplier Invoice],[Segment1],[Segment2],[Segment3] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_GLUnitLocDept_UAT] u where f.Segment1+'|'+f.Segment2+'|'+f.Segment3=u.[External Ref Code])
        """,
        """
        -- 27 account code
Select distinct [Cleansed Default Account for Supplier Invoice],[Segment4] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_Account_UAT] u where f.Segment4=u.[External Ref Code])
        """,
        """
        -- pcb and project
Select distinct [Cleansed Default Account for Supplier Invoice],[Segment5],[Segment6] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_PCBusinessUnit_Prod] u where f.Segment5=u.[External Ref Code]) and [Segment5]<>''
        """,
        """
        Select distinct [Cleansed Default Account for Supplier Invoice],[Segment5],[Segment6] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_PCBusinessUnit_Prod] u where f.Segment5+'|'+f.Segment6=u.[External Ref Code]) and [Segment6]<>''
        """,
        """
        -- activity
Select distinct [Cleansed Default Account for Supplier Invoice],[Segment7] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_Activity_UAT] u where f.Segment7=u.[External Ref Code]) and [Segment7]<>''
        """,
        """
        -- PROD checks GL
Select distinct [Cleansed Default Account for Supplier Invoice],[Segment1],[Segment2],[Segment3] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_GLUnit_Loc_Dept_Prod] u where f.Segment1=u.[External Ref Code])
        """,
        """
        Select distinct [Cleansed Default Account for Supplier Invoice],[Segment1],[Segment2],[Segment3] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_GLUnit_Loc_Dept_Prod] u where f.Segment1+'|'+f.Segment2=u.[External Ref Code])
        """,
        """
        Select distinct [Cleansed Default Account for Supplier Invoice],[Segment1],[Segment2],[Segment3] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_GLUnit_Loc_Dept_Prod] u where f.Segment1+'|'+f.Segment2+'|'+f.Segment3=u.[External Ref Code])
        """,
        """
        -- 27 account code
Select distinct [Cleansed Default Account for Supplier Invoice],[Segment4] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_Account_Prod] u where f.Segment4=u.[External Ref Code])
        """,
        """
        -- pcb and project
Select distinct [Cleansed Default Account for Supplier Invoice],[Segment5],[Segment6] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_PCBusinessUnit_Prod] u where f.Segment5=u.[External Ref Code]) and [Segment5]<>''
        """,
        """
        Select distinct [Cleansed Default Account for Supplier Invoice],[Segment5],[Segment6] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_PCBusinessUnit_Prod] u where f.Segment5+'|'+f.Segment6=u.[External Ref Code]) and [Segment6]<>''
        """,
        """
        -- activity
Select distinct [Cleansed Default Account for Supplier Invoice],[Segment7] from [dbo].[FG_Contracts_GLCodes] f where not exists (Select 'x' from [dbo].[GLString_Activity_Prod] u where f.Segment7=u.[External Ref Code]) and [Segment7]<>''
        """,
    ]
