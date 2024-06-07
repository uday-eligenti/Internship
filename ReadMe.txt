            _pricingServiceRepository.Setup(x => x.GetShippingCharge(It.IsAny<ShippingChargeRequest>()))
                .Returns(Task.FromResult(new ShippingChargeDetailsResponse()null));

--
public DateTime? GetEddFromLeadTimeDetailsForMABDShipmentItems(PriceAndShipmentDataModel priceAndShipmentDataModel, string shipmentId = null)
        {
            if (priceAndShipmentDataModel.LeadtimeDetails.IsNotNullOrEmpty())
            {
                var MABDShipment = shipmentId != null
                                      ? priceAndShipmentDataModel.Shipments.FirstOrDefault(shipment => shipment.Id == shipmentId && shipment.IsMABDShipment())
                                      : priceAndShipmentDataModel.Shipments.FirstOrDefault(shipment => shipment.IsMABDShipment());
                if (MABDShipment == null) return default;
                // salesOrder MABD item to filter the MABD leadtime details
                var salerOrderMABDItems = priceAndShipmentDataModel.Items.Where(SoItem => MABDShipment.Items.Any(shipmentItem => shipmentItem.ItemId.EqualsOrdinalIgnoreCase(SoItem.Id))).ToList();
                // using MABD Item OpenBasket item id to retrieve MABD item lead time details
                var salesOrderMABDItemsleadTimedetails = priceAndShipmentDataModel.LeadtimeDetails.Where(leadtimedetail => salerOrderMABDItems.Any(item => item.OpenBasketItemId.EqualsOrdinalIgnoreCase(leadtimedetail.OpenBasketItemId)));
                //return max edd of MABD item Lead Time details
                return salesOrderMABDItemsleadTimedetails.Where(leadtimedetail => leadtimedetail.EstimatedDeliveryDateRange.Max?.LocalDateTime != DateTime.MinValue)
               .Select(leadtimedetail => leadtimedetail.EstimatedDeliveryDateRange.Max?.LocalDateTime).Max();
            }
            return default;
        }

--
public bool IsInvalidMustArriveByDate(PriceAndShipmentDataModel priceAndShipmentDataModel, string shipmentId,string country, bool isEddFlow)
{
    if (_featureTogglesService.GetFeatureTogglesAsync().Result.IsMABDValidationApplicable && !priceAndShipmentDataModel.HasMultiShipments && !isEddFlow)
    {
        var mabdShipmentLeadtimesMaxEdd = GetEddFromLeadTimeDetailsForMABDShipmentItems(priceAndShipmentDataModel,shipmentId);

        if (mabdShipmentLeadtimesMaxEdd != null)
        {
            return !MabdHelper.MabdDateWithinRange(priceAndShipmentDataModel?.ArriveByDate ?? DateTime.MinValue, mabdShipmentLeadtimesMaxEdd ?? DateTime.MinValue, country, _mustArriveByDays);
        }
        return false;
    }
    return false;
}

--- 
This Website is for fetching the file content and displaying the content in the end point.
This application is developed using python with Flask web framework.
This app has a GET Method
The application accepts the 3 optional parameters in the URL
1. Name Of The File.
2. Starting Line to be fetched.
3. Ending Line to be fetched.

these three parameters are optional.if the user doesnt specify any of the perameter in the URL then the Applicaation chooses the Default values
the default parameter or value for file name is " file1.txt ".
the default parameter or value for starting line is 0th line.
the default parameter or value for file ending line is Nth line.


INPUT METHOD:-

url/?file_name=value&start_line=value&end_line=value

Options:-

if the user specifiles the file name which is available then the application fetches the data from the specified file.
if the specified file name is not exixt then the application raises the exception.

the user has to give the values in the URL of web page.
if no start line and end line is specified then  by default it fetches the entire content of file.
if the user enters the start line and doest enter end line then its fetching starts from start line to end of file.
if the user enters the end line and doest enter start line then its fetching starts from first line i.e 0 upto to specified end line.





This application starts uses the traditional method of python file handing.
In this applications the data is fetched and encoded in 2 ways :
	--> utf-8
	--> utf-16



-----------------------------------------------


1. commented delete opotions in dropdown
2. changed method from get to post
1. added redis page redirection for authentication
- redirect to an authentication page on clicking on redis page .. 
helping backend team
4. added perf url in  testharness ui
5. added getuser endpoint
6 add new card for clear Cache page
7 add tabs for inMemory and redis in cache page
8. redesigned cache page
9. added sticky header for key table and moved search bar to header added hide and show for it
BUG: worked on rendering issue with sahithi
10.- added table for data in inmemory
11. added funcionality for getting data for both redis and inMemory onClick of key
BUG: - solved 'page reloading on delete btn click' issue
12 fixed 'control going to default tab on key click' issue 
-13 On successful deletion we have to show a message 
14 added alert on both successful and failure of delete.
15 added close button for alert
16 raised MR with cherrypick given by sahithi
17 replaced delete options(SUCCESS,FAILURE) from hardcoded strings with enums for better code. 
18 added functionality to call get end point ,if the response has isdeleted set to true, fetch the data again for that key just to verify it is really deleted 
- In inmemory Change the name of the Delete button to Delete All
- Name of the instance column to Instance Index
- Add another column which will have delete buttons for each row
- On click of the button should call back end API (will give the endpoint later) with Service Name, Instance Index and the Cache Key
- make tab fixed height and add scroll on overflow
- add icons for deletion success or failed . for failed x and success tick for delete all and delete single instance
- added UI changes : loading animation, table scrool , adjusted styles.
BUG: solved git conflicts, fixed UI flicking issue caused by react-json-view copy button


- testing UI: found issues
	1. increase cackey input size as we can't see full key value.
	2. flip card zooming to 110% causes overflow - fixed by d-flex
	3. in sales order page : contact details tab no margin Bottom
	4. in cups validator spinner is not in center
	5. in observebility - splunk tab - card headers are not filled to 100%

- add desclaimer in inMemory
- adjust alert height
- adjust flip card links alignment
---
27/6/23:
1. commented delete opotions in dropdown
2. changed method from get to post
3. raised both MR's
4. looking into useContext



4/7/23:
1. redis page redirection for authentication
- redirect to an authentication page on clicking on redis page .. 
- waiting for valid client id from sahithi

5 to 12:- helping backend team

13/7/23:

-added perf url in  testharness
-still didn't got clientId ..so helping backend team

untill 18: added getuser endpoint

18/7/23:

- add new card for clear Cache page
- add tabs for inMemory and redis
- inMemory:
	data center dropdown:PC1,Non prod,S3B ,input feilds for pcf application,cachekey, action dropdown :get ,delete, box to show data
	one get and one delete end points added in new inMemoryCacheService.tsx, changes cachekey url , added condition for key in delete url
	mr raised and merged 

19/7/23: sahithi added sso auth changes

- redesigned cache page . moved redis key list out of tabs, 
- added sticky header for key table and moved search bar to header added hide and show for it
- worked on rendering issue with sahithi
- 

20

- added table for data in inmemory
- added funcionality for getting data for both redis and inMemory onClick of key
- solved 'page reloading on delete btn click' issue
- fixed 'control going to default tab on key click' issue 

21

- On successful deletion we have to show a message 
- added alert on both successful and failure of delete.
- added close button for alert


23

- raised MR with cherrypick given by sahithi
- replaced delete options(SUCCESS,FAILURE) from hardcoded strings with enums for better code. 
- added functionality to call get end point ,if the response has isdeleted set to true, fetch the data again for that key just to verify it is really deleted 
- mr's merged


31

- In inmemory Change the name of the Delete button to Delete All
- Name of the instance column to Instance Index
- Add another column which will have delete buttons for each row
- On click of the button should call back end API (will give the endpoint later) with Service Name, Instance Index and the Cache Key 

1/8:
- make tab fixed height and add scroll on overflow
- add icons for deletion success or failed . for failed x and success tick for delete all and delete single instance

2/8/2023
- solved git conflicts.
 worked on UI changes. 	solved git conflicts for raised mr. added UI changes : loading animation, table scrool , adjusted styles.

3/8/2023	Uday		worked on table styling. adding new functionality to compare redis and inmemory table instances.	worked on table styling. adding new functionality to compare redis and inmemory table instances.

4/8/2023	uday		adding new functionality to compare redis and inmemory table instances.	adding new functionality to compare redis and inmemory table instances.	inprogress

7/8/2023 : 
- compariosion task,
- reset inmemory onBlur of key input{

8/8/2023:

- done comparision task tested with sample inputs fix bugs

9/8/2023:

- fixed UI flicking issue caused by react-json-view copy button


14:

- testing UI: found issues
	1. increase cackey input size as we can't see full key value.
	2. flip card zooming to 110% causes overflow - fixed by d-flex
	3. in sales order page : contact details tab no margin Bottom
	4. in cups validator spinner is not in center
	5. in observebility - splunk tab - card headers are not filled to 100%
	


28:
- Sahithi clearly explained about backend task(sending same object in redis get)
- verified UI bug fixes with sahithi (done in last week)

29:
- add desclaimer in inMemory
- adjust alert height
- adjust flip card links alignment

30,31: 
- (sending same object in redis get) deserializing data 



5-9-23 - 8-9-23:
-> exploring teams api and gitlap api

26/9/23:
-> adding p11,s11 datacenter links in both frontend and backend

12/10/23:

-> tested previous mr on UI inmemory cache . found errors for some pcf apps.
-> fixed loading spinner not comming on key change issue
-> tested changes of backend for 1st bug
-> working on delete btn access condition
NonProdRead , ProdRead--- no delete button

NonProdReadWrite --- delete button only in Non prod

 ProdReadWrite -- delete button in both 
16/10/23:
-> tested delete access by changing my access in backend api

17:
-> solved comments 
-> working on UI bugs found in redis and in memory:
(Delete notification issue with redis,The dropdown items are not getting reset in in memory in some cases,In memory on delete tick icon is not going even after the data is reset)

18:
-> removed comments,logs.solved alert and tick icon issues. mr raised
------------------------
req
---------------

21/10/2023-20/12/2023:

worked on code coverage of ship service

19/2/24:

new devops team with sajan


20/02/24:
1. worked on UI issue in redis page.(showing not connected icon for a second in redispage onload)

21/02.24:
1. working on GetUsers UI page.
2. worked on adding backend endpoint with pardu.



22/02/24:

1. worked on getUsers endpoint(backend).
2. integrated backend to users front end page
3. added icons, sorting in user table
4. deployed and tested changes
5. started DAD score report page designing.

23/02/24:

1. working on DAD status report page
2. added refresh functionality
3. added download to excel functionality
4. added present and previous score functionality(temporary)

-------------
21/03/24:
got into new team.
1. call with pranita. they work on handling ux of entire unified checkout mfe. with html css js
2. kt from 22 march.

------------------
UX TEAM DEFECTS:
1.CCMF-4086
[Premier Convergence FED] [V4]:[G4] Spacing issue on thank you page
2. CCMF-4497
DDS2.0-Change radio button label color to #0E0E0E
3. CCMF-5018
Segment-selector- typography changes
4. CCS-5910
The credit card type images lack alt text, making them inaccessible to screen reader users
5. CCS-5937: Extra gap is coming between standard delivery date and mabd data section
6. CCS-6450
typography changes - Change the title "Shipping"
