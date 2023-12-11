--
return twoTouchItems.All(item => fulfillmentChoiceResponse.OutputItems
                                  .FirstOrDefault(opItem => opItem.ItemId.EqualsOrdinalIgnoreCase(item.ItemId))
                                  .ShippingOptions.Any(shpOp => shpOp.OptionId.EqualsOrdinalIgnoreCase(item.TwoTouchShippingMethod)));
--

            _itemHelperMock.Setup(itemhelper => itemhelper.GetChildItems(It.IsAny<string>(), It.IsAny<IEnumerable<ItemSnapshotDetail>>(), It.IsAny<List<ItemSnapshotDetail>>())).Returns(new List<ItemSnapshotDetail>() { new ItemSnapshotDetail() { ItemId = "ItemId1" } });

 System.ArgumentNullException : Value cannot be null. (Parameter 'collection')
---
       public override async Task<bool> UpdateShipmentForShippingChoice(IEnumerable<IGrouping<string, ItemLevelShippingChoice>> shippingChoiceGroups, SalesOrderDataModel salesOrder, Contact contact, ShipmentShippingChoiceRequest request,
           string shippingInstructions, string[] othersShippingOptions, List<LeadTimeDetail> leadTimeDetails)
       {
           //Add FDD & extended Properties for FDD
           var largerOrderItems = request?.ItemLevelShippingChoices.Where(c => c.IsLargeOrder);
           if (largerOrderItems.Any())
           {
               var itemsSupportablityInfo = new Dictionary<string, string>();
               itemsSupportablityInfo = largerOrderItems.Select(cond => new KeyValuePair<string, string>(cond.ItemId, cond.Supportability)).ToDictionary(dict => dict.Key, dict => dict.Value);
               await AddFddSalesOrderExtendedProperties(
                   request.Context.Country,
                   request.SalesOrderId,
                   largerOrderItems.Any(),
                   itemsSupportablityInfo,
                   salesOrder.GetLargeOrderExtendedProperties());
           }

           if (_featureTogglesService.GetFeatureTogglesAsync().Result.IsUSShipmentsFlow && salesOrder.Shipments.Any() && shippingChoiceGroups.Any())
           {
               if (!_featureTogglesService.GetFeatureTogglesAsync().Result.IsClearAndCreateShipmentsEnabled)
                   return await UpdateShipmentsForShippingChoice(shippingChoiceGroups, salesOrder, contact, request, shippingInstructions, othersShippingOptions, leadTimeDetails);

               if (salesOrder.Shipments.Count > 1 && shippingChoiceGroups.Count() == 1 && shippingChoiceGroups.FirstOrDefault().All(item => !item.IsTwoTouchItem) && shippingChoiceGroups.FirstOrDefault().Any(item => item.IsMABDItem))
                   return await ClearAndCreateShipments();

               return await ModifyShipments(shippingChoiceGroups, salesOrder, contact, request, shippingInstructions, othersShippingOptions, leadTimeDetails);
           }

           return await base.UpdateShipmentForShippingChoice(shippingChoiceGroups, salesOrder, contact, request, shippingInstructions, othersShippingOptions, leadTimeDetails);

           async Task<bool> ClearAndCreateShipments()
           {
               var clearShipments = await ClearShipments(salesOrder.Id, salesOrder.Shipments);
               if (!clearShipments) return false;

               var shippingChoiceGroup = shippingChoiceGroups.FirstOrDefault();
               var allItems = shippingChoiceGroup.ToList();

               //Create Ready-Stock Shipment
               var readyStockItems = allItems?.Where(item => item.IsPickOrder);
               if (IsReadyStockEnabled(request.Context?.IsPremierCustomer ?? false) && readyStockItems.Any())
               {
                   var readyStockParentItems = readyStockItems?.Where(x => x.ParentItemId.IsNullOrEmpty() || x.ParentItemId == Guid.Empty.ToString())?.ToList();
                   var allChildItems = allItems?.Where(x => !x.ParentItemId.IsNullOrEmpty() && x.ParentItemId != Guid.Empty.ToString())?.ToList();

                   foreach (var parentItem in readyStockParentItems)
                   {
                       var readyStockItemsParentAndChild = new List<ItemLevelShippingChoice>();
                       readyStockItemsParentAndChild.AddRange(_itemHelper.GetChildItems(parentItem.ItemId, allChildItems, new List<ItemLevelShippingChoice>()));
                       readyStockItemsParentAndChild.Add(parentItem);

                       var createReadyStockShipment = await CreateShipmentAndLeadTimeOnShippingChoiceUpdate(shippingChoiceGroup.Key, shippingChoiceGroup.FirstOrDefault().ShipmentName,
                           contact, readyStockItemsParentAndChild, request, salesOrder, othersShippingOptions, leadTimeDetails,
                           arriveByDate: readyStockItemsParentAndChild.Any(item => item.IsMABDItem) ? readyStockItemsParentAndChild.Select(item => item.EstimatedDeliveryDateMax).Max() : null);
                       allItems?.RemoveAll(item => readyStockItemsParentAndChild.Any(y => y.ItemId.Equals(item.ItemId)));

                       if (!createReadyStockShipment) return false;
                   }
               }

               //Create MABD Shipment
               var mabdShippingChoiceItems = allItems?.Where(item => item.IsMABDItem && !item.IsPickOrder);

               var arriveByDate = mabdShippingChoiceItems.Select(item => item.EstimatedDeliveryDateMax).Max();

               var createMABDShipment = await CreateShipmentAndLeadTimeOnShippingChoiceUpdate(shippingChoiceGroup.Key, shippingChoiceGroup.FirstOrDefault().ShipmentName,
                   contact, mabdShippingChoiceItems.ToList(), request, salesOrder, othersShippingOptions, leadTimeDetails, arriveByDate);
               allItems.RemoveAll(item => mabdShippingChoiceItems.Any(y => y.ItemId.Equals(item.ItemId)));
               if (!createMABDShipment) return false;

               //Create non-MABD Shipment
               var nonMabdShippingChoiceItems = allItems?.Where(item => !item.IsMABDItem && !item.IsPickOrder);

               var createNonMABDShipment = await CreateShipmentAndLeadTimeOnShippingChoiceUpdate(shippingChoiceGroup.Key, shippingChoiceGroup.FirstOrDefault().ShipmentName,
                   contact, nonMabdShippingChoiceItems.ToList(), request, salesOrder, othersShippingOptions, leadTimeDetails);
               if (!createNonMABDShipment) return false;

               return true;
           }
       }
---

 private async Task<bool> ModifyShipments(SalesOrderDataModel salesOrder, ShipmentRequest shipmentRequest)
 {
     var incotermsSeelction = shipmentRequest.IncotermsSelection != null ? shipmentRequest.IncotermsSelection : salesOrder.GetIncotermsSelection();
     var fulfillmentChoiceServiceRequest = _shipmentChoiceService.FulfillmentChoiceServiceRequestMapper(shipmentRequest.Context, shipmentRequest.ShippingContact,
                             shipmentRequest.ItemSnapshotDetails, salesOrder.PaymentMethods,
                             salesOrder.Id, false, null, selectedShippingOption: null, false, false, incotermsSeelction);
     var fulfillmentChoiceResponse = await _shipmentChoiceService.GetFulfillmentChoice(fulfillmentChoiceServiceRequest);

     var deltaShipments = new List<SalesOrderShipment>();

     var deltaShipGroups = new List<ShippingChoiceGroup>();
     var shipments = _twoTouchService.GetAllNon2TShipments(salesOrder.Shipments, shipmentRequest);

     var shippingChoiceGroupsWithOutput = new List<ItemSnapshotDetailWithOutputItem>();
     foreach (var itemSnapshotDetail in _twoTouchService.GetAllNon2TItemSnapshotDetails(shipmentRequest))
     {
         var (outputItem, shippingChoice) = GetValidShippingChoice(itemSnapshotDetail.ItemId, itemSnapshotDetail.SaleOrderItemId);
         shippingChoiceGroupsWithOutput.Add(new ItemSnapshotDetailWithOutputItem
         {
             ItemSnapshotDetail = itemSnapshotDetail,
             OutputItem = outputItem,
             ValidShippingChoice = shippingChoice,
             ShipmentName = GetShipmentName(shippingChoice)
         });
     }

     var leadTimeDetails = new List<LeadTimeDetail>();
     var shippingChoiceGroups = GetShippingGroups(shippingChoiceGroupsWithOutput, shipmentRequest.Context?.IsPremierCustomer ?? false);
     var contact = shipments.FirstOrDefault()?.ShippingContact;
     var othersShippingOptions = shipments?.FirstOrDefault()?.ShippingOptions?.ToArray();

     var shippingInstructions = shipmentRequest.ShippingInstructions ?? shipments.FirstOrDefault()?.Instructions;
     if (shippingInstructions != null)
         shipmentRequest.ShippingInstructions = shippingInstructions;

     if (shipments.Count == shippingChoiceGroups.Count)
     {
         var updateShipmentFromGroupsStatus = await UpdateShipmentFromGroups(shipments, shippingChoiceGroups);
         if (!updateShipmentFromGroupsStatus) return false;
         await _leadTimeDetailsService.UpdateLeadTimeDetailsToSalesOrder(leadTimeDetails, fulfillmentChoiceResponse.MaxLeadTimeItemId.ToString(), salesOrder.Id);
         return true;
     }

     if (shipments.Count > shippingChoiceGroups.Count)
     {
         var shipmentsToBeUpdated = shipments.Take(shippingChoiceGroups.Count).ToList();
         var updateShippingChoiceGroup = await UpdateShipmentFromGroups(shipmentsToBeUpdated, shippingChoiceGroups);
         if (!updateShippingChoiceGroup) return false;
         deltaShipments = shipments.Where(shipment => !shipmentsToBeUpdated.Any(shp => shp.Id.EqualsOrdinalIgnoreCase(shipment.Id)))?.ToList();
     }

     else if (shipments.Count < shippingChoiceGroups.Count)
     {
         var groupsToBeUpdated = shippingChoiceGroups.Take(shipments.Count);
         var updateShippingChoiceGroup = await UpdateShipmentFromGroups(shipments, groupsToBeUpdated);
         if (!updateShippingChoiceGroup) return false;
         shippingChoiceGroups.RemoveRange(0, shipments.Count);
         deltaShipGroups = shippingChoiceGroups;
     }

     if (deltaShipments.Any())
     {
         var clearShipments = await ClearShipments(salesOrder.Id, deltaShipments);
         if (!clearShipments) return false;
     }

     if (deltaShipGroups.Any())
     {
         var addNewShipmentsStatus = await AddNewShipments(deltaShipGroups);
         if (!addNewShipmentsStatus) return false;
     }

     return true;

     string GetShipmentName(string optionId)
     {
         var shippingOptionContent = _shippingOptionContentBuilder.MapContent(shipmentRequest.ShippingOptionContent);
         var shippingDetail = fulfillmentChoiceResponse.CommonShippingDetails?.FirstOrDefault(x => x.Options.Any(y => y.OptionId == optionId));
         var ShipmentName = !fulfillmentChoiceResponse.IsFallBackResult && shippingDetail != null ?
                                 shippingOptionContent?.DeliveryOptions?.GetValueOrDefault(shippingDetail?.OptionCode) ?? shippingDetail?.Description : shippingOptionContent?.Strings?.DefaultShippingMethodDescription;
         return ShipmentName;
     }

     List<ShippingChoiceGroup> GetShippingGroups(List<ItemSnapshotDetailWithOutputItem> shippingChoiceGroupsWithOutput, bool IsPremierCustomer)
     {
         var shippingChoiceGroups = new List<ShippingChoiceGroup>();

         foreach (var shippingGroup in shippingChoiceGroupsWithOutput?.GroupBy(shippingChoice => shippingChoice.ValidShippingChoice))
         {
             var shippingChoiceGroupItems = shippingGroup.ToList();
             var readyStockItems = shippingGroup?.Where(x => x.ItemSnapshotDetail.IsPickOrder)?.ToList();

             if (IsReadyStockEnabled(IsPremierCustomer) && readyStockItems.Any())
             {
                 var readyStockParentItems = readyStockItems?.Where(x => x.ItemSnapshotDetail.ParentItemId.IsNullOrEmpty() || x.ItemSnapshotDetail.ParentItemId == Guid.Empty.ToString())?.ToList();
                 var allChildItems = shippingChoiceGroupItems?.Where(x => !x.ItemSnapshotDetail.ParentItemId.IsNullOrEmpty() && x.ItemSnapshotDetail.ParentItemId != Guid.Empty.ToString())?.ToList();

                 foreach (var parentItem in readyStockParentItems)
                 {
                     var readyStockItemsParentAndChild = new List<ItemSnapshotDetailWithOutputItem>();
                     readyStockItemsParentAndChild.AddRange(_itemHelper.GetChildItems(parentItem.ItemSnapshotDetail.ItemId, allChildItems, new List<ItemSnapshotDetailWithOutputItem>()));
                     readyStockItemsParentAndChild.Add(parentItem);

                     shippingChoiceGroups.Add(new ShippingChoiceGroup
                     {
                         ShippingChoice = shippingGroup.Key,
                         ItemSnapshotDetailWithOutputItems = readyStockItemsParentAndChild
                     });

                     shippingChoiceGroupItems.RemoveAll(x => readyStockItemsParentAndChild.Any(y => y.ItemSnapshotDetail.ItemId.Equals(x.ItemSnapshotDetail?.ItemId)));
                 }
             }

             if (!shippingChoiceGroupItems.IsNullOrEmpty())
             {
                 shippingChoiceGroups.Add(new ShippingChoiceGroup
                 {
                     ShippingChoice = shippingGroup.Key,
                     ItemSnapshotDetailWithOutputItems = shippingChoiceGroupItems
                 });
             }
         }
         return shippingChoiceGroups;
     }

     (OutputItem outputItem, string shippingChoice) GetValidShippingChoice(string itemId, string saleOrderItemId)
     {
         var shippingChoice = shipments.FirstOrDefault(x => x.Items.Any(a => a.ItemId == saleOrderItemId))?.ShippingMethod;
         var itemDetail = fulfillmentChoiceResponse.OutputItems.FirstOrDefault(item => item.ItemId == itemId);
         if (!itemDetail.ShippingOptions.Any(x => x.OptionId == shippingChoice))
         {
             shippingChoice = GetShippingChoice(shipmentRequest.Context.IsPremierCustomer, fulfillmentChoiceResponse, itemId);
         }
         return (itemDetail, shippingChoice);
     }

     async Task<bool> UpdateShipmentFromGroups(List<SalesOrderShipment> shipments, IEnumerable<ShippingChoiceGroup> shippingGroups)
     {
         int index = 0;
         foreach (var shippingChoiceGroup in shippingGroups)
         {
             var updateShipmentStatus = await UpdateShipmentFromItemSnapshotDetail(shipments[index], shippingChoiceGroup.ShippingChoice, shippingChoiceGroup.ItemSnapshotDetailWithOutputItems, shipmentRequest.ShippingContact, shipmentRequest,
                 shipmentRequest.ShippingInstructions, leadTimeDetails, salesOrder, fulfillmentChoiceResponse);
             if (!updateShipmentStatus) return false;
             index++;
         }

         return true;
     }

     async Task<bool> AddNewShipments(List<ShippingChoiceGroup> deltaShippingChoiceGroups)
     {
         foreach (var shippingChoiceGroup in deltaShippingChoiceGroups)
         {
             var createShipmentResult = await CreateShipmentAndLeadTimeOnUpdateAddress(shippingChoiceGroup.ShippingChoice, shippingChoiceGroup.ItemSnapshotDetailWithOutputItems.FirstOrDefault().ShipmentName,
                 shipmentRequest.ShippingContact, shippingChoiceGroup.ItemSnapshotDetailWithOutputItems.Select(x => x.ItemSnapshotDetail).ToList(), shipmentRequest, fulfillmentChoiceResponse.OutputItems, othersShippingOptions, leadTimeDetails);
             if (!createShipmentResult) return false;
         }

         return true;
     }
 }
--
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

public async Task<bool> CreateOrUpdateShipment(QuoteShipmentRequest shipmentRequest)
        {
            var quote = await GetQuoteAsync(shipmentRequest.QuoteId);
            shipmentRequest.Context = await _shippingContactService.AssignCustomerNumbers(shipmentRequest.Context, quote);
            if (quote.Shipments.IsNullOrEmpty())
            {
                var createRequest = _quoteShippingMapper.MapQuoteShipmentCreationRequest(shipmentRequest, quote);
                return await _quoteShipmentServiceFactory.GetShipmentService(shipmentRequest.Context?.Region).CreateQuoteShipments(createRequest);
            }
            if (quote.Shipments.Count == 1)
            {
                shipmentRequest.SelectedShippingOption = quote.Shipments.First().ShippingMethod;
            }
            return await _quoteShipmentServiceFactory.GetShipmentService(shipmentRequest.Context?.Region).UpdateQuoteShipments(shipmentRequest, quote);
        }
--------------
public async Task<bool> DeleteShipments(string quoteId, List<QuoteShipment> shipments, List<QuoteMultishipmentOperationDetail> multishipmentOperationDetails = null, bool isEnableMultishipmentOperationEndpoint = false)
        {
            foreach (var shipment in shipments)
            {
                if (isEnableMultishipmentOperationEndpoint)
                {
                    QuoteCreateOrUpdateShipmentRequest createShipment = new QuoteCreateOrUpdateShipmentRequest();
                    createShipment.ShipmentId = shipment.Id;
                    multishipmentOperationDetails.Add(MapQuoteMultishipmentsDetails(createShipment, PatchOperationType.Remove));
                }
                else
                {
                    var clearshipment = await _quoteRepository.DeleteShipment(quoteId, shipment.Id);
                    if (!clearshipment) return false;
                }
            }
            return true;
        }

--
public async Task<bool> UpdateVatpNotes(QuoteVatpNotesRequest request)
        {
            var quote = await GetQuoteAsync(request.QuoteId);
            bool result = true;
            if (quote != null)
            {
                foreach (var shipment in quote.Shipments)
                {
                    result = await _quoteShipmentService.UpdateShipment(new QuoteShipmentUpdationRequest
                    {
                        ShipmentId = shipment.Id,
                        DeliveryMethod = shipment.ShippingMethod,
                        Context = request.Context,
                        VatpNotes = request.VatpNotes
                    }, request.QuoteId, quote, multishipmentOperationList);
                }
                await PatchQuoteMultishipments(multishipmentOperationList, quote.Id);
            }
            return result;
        }

--
async Task<bool> CreateShippingChoiceShipment(IGrouping<string, ItemLevelShippingChoice> shippingChoiceGroup)
            {
                var createQuoteRequest = _quoteShippingMapper.MapQuoteShippingChoiceRequest(quoteShipment, shippingChoiceGroup, request);
                createQuoteRequest.Items = BuildQuoteItemDetails(shippingChoiceGroup.ToList(), quote, request.SkipShipmentItemDetails);
                createQuoteRequest.FuturisticDeliveryDate = fdd;
                if (isEnableMultishipmentOperationEndpoint)
                {
                    multishipmentOperationList.Add(MapQuoteMultishipmentsDetails(createQuoteRequest, PatchOperationType.Modify));
                    return true;
                }
                else
                {
                    return await _quoteRepository.CreateQuoteShipment(createQuoteRequest, request.QuoteId);
                }
            }
---------
 public SalesOrderUpdateShipmentRequest GetUpdateShipmentsRequest(MultiShipServiceShipment multiShipmentRequest, string shipmentId,
            string[] shippingOptions, FulfillmentChoiceContext context, Dictionary<string, string> salesOrderExtendedProperties, string salesOrderId = "")
        {
            List<ShipmentItemReference> shipmentItems;
            string shipmentMethod, shipmentName, shippingInstructions, estimatedDeliveryDateMax, installationInstructions;
            DesignatedCarrier designatedCarrier;
            var shippingContactReferences = _shippingContactService.GetContactReference(context, multiShipmentRequest?.ShippingContact?.ContactReferenceUrl);
            GetMultiShipmentRequest(multiShipmentRequest, out shipmentItems, out shipmentMethod, out shipmentName, out shippingInstructions,
                out designatedCarrier, out estimatedDeliveryDateMax, out installationInstructions);
            //Reset MABD invalid Extended Property
            if ((context.Region.ToUpper() == "EMEA" || context.Region.ToUpper() == "APJ") && !string.IsNullOrWhiteSpace(salesOrderId))
            {
                salesOrderExtendedProperties.TryGetValue(ExtendedPropertyKeys.IsInvalidMustArriveByDate + "-" + shipmentId, out string keyValue);
                if (!string.IsNullOrEmpty(keyValue) && keyValue.EqualsOrdinalIgnoreCase("true"))
                    _salesOrderServiceRepository.PutExtendedProperty(salesOrderId, ExtendedPropertyKeys.IsInvalidMustArriveByDate + "-" + shipmentId, "false");
                salesOrderExtendedProperties.TryGetValue(ExtendedPropertyKeys.IsInvalidMabdWhenPaymentApplied + "-" + shipmentId, out string triggredValue);
                if (!string.IsNullOrEmpty(triggredValue) && triggredValue.EqualsOrdinalIgnoreCase("true"))
                    _salesOrderServiceRepository.PutExtendedProperty(salesOrderId, ExtendedPropertyKeys.IsInvalidMabdWhenPaymentApplied + "-" + shipmentId, "false");
            }
            return new SalesOrderUpdateShipmentRequest
            {
                ShipmentId = shipmentId,
                ShippingMethod = shipmentMethod,
                ShipmentName = shipmentName,
                ShippingContact = (context != null && context.IsShippingContactDeprecated) ? null : multiShipmentRequest?.ShippingContact,
                Instructions = shippingInstructions,
                Items = shipmentItems?.ToArray(),
                ShippingOptions = shippingOptions,
                DesignatedCarrier = designatedCarrier,
                InboundShipMethod = null,
                InstallationInstructions = installationInstructions,
                GroupId = multiShipmentRequest.GroupId,
                ContactReferences = shippingContactReferences,
                ArriveByDate = GetMABDForSaleOrder(multiShipmentRequest, context),
                FuturisticDeliveryDate = GetFDDForSaleOrder(multiShipmentRequest)
            };
    }



------        [Fact]
        public void GetQuoteOperationsRequest_ReturnsValidOperationDetailForCreate()
        {
            // Arrange
            var multiShipServiceShipment = new QuoteMultiShipServiceShipment
            {
                ShipmentShippingChoice = new QuoteShipmentShippingChoiceRequest
                {
                    ItemLevelShippingChoices = new List<QuoteItemLevelShippingChoice>
                {
                    new QuoteItemLevelShippingChoice { OptionId = "Option1" }
                },
                    DesignatedCarrier = new DesignatedCarrier {  },
                    ShipmentName = "Shipment123",
                    ShippingInstructions = "Handle with care",
                    InstallationInstructions = "Install carefully",
                },
                ShippingContact = new Models.Common.Shipping.Contact {  },
                GroupId = "Group123"
            };

            string shipmentId = "ShipmentId123";
            PatchOperationType operationType = PatchOperationType.Add;

            // Act
            var result = _sut.GetQuoteOperationsRequest(multiShipServiceShipment, shipmentId, operationType);

            // Assert
            Assert.NotNull(result);
            Assert.Equal(operationType, result.OperationType);
            Assert.Equal(shipmentId, result.ResourceId);
            Assert.NotNull(result.Value);
            Assert.Equal("Option1", result.Value.ShippingMethod);
            Assert.Equal("Shipment123", result.Value.ShipmentName);
            Assert.Equal("Handle with care", result.Value.Instructions);
            Assert.Equal("Install carefully", result.Value.InstallationInstructions);
            Assert.NotNull(result.Value.Items);
            Assert.Equal("Group123", result.Value.GroupId);
        }




public QuoteMultishipmentOperationDetail GetQuoteOperationsRequest(QuoteMultiShipServiceShipment multiShipServiceShipment, string shipmentId, PatchOperationType operationType)
        {
            string shipmentMethod = multiShipServiceShipment?.ShipmentShippingChoice?.ItemLevelShippingChoices[0]?.OptionId;
            return new QuoteMultishipmentOperationDetail
            {
                OperationType = operationType,
                ResourceId = shipmentId,
                Value = new QuoteCreateOrUpdateShipmentRequest()
                {
                    FuturisticDeliveryDate = multiShipServiceShipment?.ShipmentShippingChoice != null ? GetFDDForQuote(multiShipServiceShipment) : String.Empty,
                    ShippingContact = multiShipServiceShipment?.ShippingContact,
                    InstallationInstructions = multiShipServiceShipment?.ShipmentShippingChoice?.InstallationInstructions,
                    Items = multiShipServiceShipment?.ShipmentShippingChoice != null ? BuildQuoteItemDetails(multiShipServiceShipment?.ShipmentShippingChoice?.ItemLevelShippingChoices) : null,
                    ShippingMethod = shipmentMethod,
                    DesignatedCarrier = shipmentMethod.IsNotNullOrEmpty() ? shipmentMethod.EqualsOrdinalIgnoreCase(DeliveryMethodsConstants.DesignatedCarrierCode) 
                ? multiShipServiceShipment?.ShipmentShippingChoice?.DesignatedCarrier ?? new DesignatedCarrier() : null : null,
                    ShipmentName = multiShipServiceShipment?.ShipmentShippingChoice?.ShipmentName,
                    Instructions = multiShipServiceShipment?.ShipmentShippingChoice?.ShippingInstructions,
                    GroupId = multiShipServiceShipment?.GroupId
                }
            };
        }


--------
        public ExtendedPropertiesCollection GetFddtExtendedProperties(ExtendedPropertiesCollection extendedPropertiesCollection, string country, bool isLargeOrder, Dictionary<string, string> itemSupportabilityInfo = null, Dictionary<string, string> existingSalesOrderExtendedProperties = null)
        {
            if (isLargeOrder)
            {
                extendedPropertiesCollection.Add(ExtendedPropertyKeys.IsLargeOrder, isLargeOrder.ToString().ToLower());
                if (country?.ToUpper() == "US" || country?.ToUpper() == "CA")
                {
                    //Remove exitsing extended Properties and Reset if LargeOrder for part
                    if (existingSalesOrderExtendedProperties != null)
                    {
                        var extendedPropertiesSupportability = existingSalesOrderExtendedProperties.Where(c => c.Key.Contains("Supportability"));
                        extendedPropertiesSupportability.ToList().ForEach(c =>
                        {
                            extendedPropertiesCollection.Add(c.Key, string.Empty);
                        });
                    }
                    if (itemSupportabilityInfo != null)
                    {
                        itemSupportabilityInfo.ForEach(item =>
                        {
                            if (existingSalesOrderExtendedProperties != null && existingSalesOrderExtendedProperties.ContainsKey(string.Format(ExtendedPropertyKeys.Supportability, item.Key)))
                            {
                                extendedPropertiesCollection.ExtendedProperties.FirstOrDefault(c => c.Key.Equals(string.Format(ExtendedPropertyKeys.Supportability, item.Key))).Value = JsonConvert.SerializeObject(new GenericField { FieldKey = "Supportability", FieldValue = item.Value });
                            }
                            else
                                extendedPropertiesCollection.Add(string.Format(ExtendedPropertyKeys.Supportability, item.Key), JsonConvert.SerializeObject(new GenericField { FieldKey = "Supportability", FieldValue = item.Value }));
                        });
                    }
                }
            }
            else
            {
                if (existingSalesOrderExtendedProperties != null)
                {
                    //Remove exitsing extended Properties by setting to empty
                    extendedPropertiesCollection.Add(ExtendedPropertyKeys.IsLargeOrder, string.Empty);
                    if (country?.ToUpper() == "US" || country?.ToUpper() == "CA")
                    {
                        var extendedPropertiesSupportability = existingSalesOrderExtendedProperties.Where(c => c.Key.Contains("GenericField[FieldKey='Supportability']"));
                        extendedPropertiesSupportability.ToList().ForEach(c =>
                        {
                            extendedPropertiesCollection.Add(c.Key, string.Empty);
                        });
                    }
                }
            }
            return extendedPropertiesCollection;
        }
--
 public async Task<QuoteDataModel> GetQuoteAsync(string quoteId)
 {
     ValidateSourceId(quoteId);
     var quoteUri = _quoteConfigurationSettings.GetRequestUri(QuoteEndpointVersion, quoteId);
     using (var cancellationTokenSource = new CancellationTokenSource(requestTimeout))
     {
         HttpResponseMessage quoteResponse = new HttpResponseMessage();
         try
         {
             cancellationTokenSource.Token.ThrowIfCancellationRequested();
             quoteResponse = await _quoteClient.GetAsync(quoteUri, cancellationTokenSource.Token);

             if (!quoteResponse.IsSuccessStatusCode)
             {
                 return default;
             }

             return JsonConvert.DeserializeObject<QuoteDataModel>(await quoteResponse.Content.ReadAsStringAsync());
         }
         catch (OperationCanceledException ex)
         {
             throw new Exception(ExceptionLog.LogException(ex.ToString(), quoteResponse));
         }
     }


        // g
        [Fact]
        public async Task GetQuoteAsync_catch()
        {
            //arrange

            //action
            await Assert.ThrowsAsync<Exception>(() => _sut.GetQuoteAsync("quote"));
        }
 Message: 
   System.NotSupportedException : Unsupported expression: c => c.GetAsync(It.IsAny<Uri>(), QuoteRepositoryTests.<>c__DisplayClass16_0.cancellationTokenSource.Token)
   Non-overridable members (here: HttpClient.GetAsync) may not be used in setup / verification expressions.

        //
Message: 
  Assert.Throws() Failure
  Expected: typeof(System.Exception)
  Actual:   typeof(Moq.MockException): HttpMessageHandler.SendAsync(Method: GET, RequestUri: 'http://g2vmquosvc01.olqa.preol.dell.com:1006/V3/quotes/quote', Version: 1.1, Content: <null>, Headers:
  {
    Authorization: test 1234
  }, CancellationToken) invocation failed with mock behavior Strict.
