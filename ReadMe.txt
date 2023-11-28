---
  public bool IsTwoTouchSupportedItem(OutputItem outputItem, List<ItemSnapshotDetail> itemSnapshotDetails, bool isPremierCustomer, out bool isSupportedShipMethod)
        {
            isSupportedShipMethod = false;
            if (IsTwoTouchProduct(isPremierCustomer, itemSnapshotDetails))
            {
                ItemSnapshotDetail itemSnapShot = itemSnapshotDetails.FirstOrDefault(ele => ele.ItemId.EqualsOrdinalIgnoreCase(outputItem.ItemId));
                if (itemSnapShot.IsTwoTouchItem)
                {
                    isSupportedShipMethod = Is2TSupportedShipMethod(outputItem, itemSnapShot.TwoTouchShippingMethod);
                    return true;
                }
            }
            return false;
        }--
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
