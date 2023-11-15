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
-----------------
    var _loggerMock = new Mock<IShippingMethodLogger>();
    var salesOrderId = "exampleSalesOrderId";
    string nullMaxLeadTimeItemId = null;
    _loggerMock.Setup(x => x.LogWarningMessage(It.IsAny<string>())); 
    // Action
    await _leadTimeDetailsService.UpdateLeadTimeDetailsToSalesOrder(
        new List<LeadTimeDetail> { new LeadTimeDetail() }, nullMaxLeadTimeItemId, salesOrderId);
    // Assert
    _loggerMock.Verify(
x => x.LogWarningMessage(It.IsAny<string>()),
Times.Once);

if (maxLeadTimeItemId.IsNullOrEmpty())
    _logger.LogWarningMessage($"UpdateLeadTimeDetailsToSalesOrder: MaxLeadTimeId is null for the SalesOrderId: {salesOrderId}");
--
 public async Task<bool> UpdateLeadTimeDetailsToSalesOrder(List<LeadTimeDetail> leadTimeDetails, string maxLeadTimeItemId, string salesOrderId)
 {           

     if (salesOrderId.IsNullOrEmpty())
         throw new ArgumentNullException(nameof(salesOrderId));

     if (maxLeadTimeItemId.IsNullOrEmpty())
         _logger.LogWarningMessage($"UpdateLeadTimeDetailsToSalesOrder: MaxLeadTimeId is null for the SalesOrderId: {salesOrderId}");

     var salesOrderPatchLeadTimeRequest = _leadTimeDetailsRequestBuilder.BuildRequest(leadTimeDetails, maxLeadTimeItemId);

     return await _salesOrderServiceRepository.PutLeadTimeDetailsToSalesOrder(salesOrderPatchLeadTimeRequest, salesOrderId);           
 }
-----------------------------------------------------------------------
public async Task<CartContextDetails> GetUserContext(string salesOrderId)
        {
            if (salesOrderId == null)
            {
                throw new ArgumentNullException("Sales order ID cannot be null");
            }

            var salesOrder = await _salesOrderServiceRepository.GetSalesOrderAsync(salesOrderId);

            if (salesOrder != null)
            {
                var cartOrQuoteId = salesOrder.References.FirstOrDefault()?.Target.Split("/").Last();

                var cart = await _cartService.GetCartAsync(cartOrQuoteId); 

                if (cart != null)
                {
                    return new CartContextDetails
                    {
                        CartOrQuoteId = cartOrQuoteId,
                        Context = new FulfillmentChoiceContext()
                        {
                            Country = cart.CommerceContext?.Country,
                            Currency = cart.CommerceContext?.Currency,
                            Region = cart.CommerceContext?.Region,
                            Segment = cart.CommerceContext?.Segment,
                            CurrencyCultureInfo = $"{cart.CommerceContext?.Language}-{cart.CommerceContext?.Country}",
                            CustomerSet = cart.CommerceContext?.CustomerSet,
                            AccessGroup = cart.CommerceContext?.AccessGroup,
                            SourceApplicationName = cart.CommerceContext?.SourceApplicationName,
                            BusinessUnitId = cart.CommerceContext?.BusinessUnitId,
                            CompanyNumber = cart.CommerceContext?.CompanyNumber,
                            IsGop = cart.CommerceContext?.IsGOP ?? false                            
                        }
                    };
                }
            }
            return default;
        }
test:
 public async Task GetUserContext_ThrowsArgumentNullException_WhenSalesOrderIdIsNull()
        {
            await Assert.ThrowsAsync<ArgumentNullException>(()=> _itemService.GetUserContext(null));
        }

        [Fact]
        public async Task GetUserContext_ShouldReturnCartContextDetails_ForValidRequest()
        {
            _salesOrderServiceRepository.Setup(x => x.GetSalesOrderAsync(It.IsAny<string>()))
                .ReturnsAsync(new Models.SalesOrder.SalesOrder() 
                { 
                    References = new List<Models.SalesOrder.Reference>()
                    {
                        new Models.SalesOrder.Reference()
                        {
                            Target = "foo/salesOrderID"
                        }
                    }    
                });

            var context = new CommerceContext()
            {
                Country = "US",
                Currency = "currency",
                Region = "Region",
                Segment = "Segment",
                Language = "en",
                CustomerSet = "CustomerSet",
                SourceApplicationName = "SourceApplication",
                BusinessUnitId = "1",
                CompanyNumber = "2",
                IsGOP = true
            };

            _cartService.Setup(x => x.GetCartAsync(It.IsAny<string>()))
                .ReturnsAsync(new V3Cart()
                {
                    CommerceContext = context
                });

            var result = await _itemService.GetUserContext("salesOrderId");

            Assert.NotNull(result);
            Assert.Equal(context.Country, result.Context.Country);
            Assert.Equal(context.Currency, result.Context.Currency);
            Assert.Equal(context.Region, result.Context.Region);
            Assert.Equal(context.Segment, result.Context.Segment);
            Assert.Equal($"{context.Language}-{context.Country}", result.Context.CurrencyCultureInfo);
            Assert.Equal(context.CustomerSet, result.Context.CustomerSet);
            Assert.Equal(context.AccessGroup, result.Context.AccessGroup);
            Assert.Equal(context.SourceApplicationName, result.Context.SourceApplicationName);
            Assert.Equal(context.BusinessUnitId, result.Context.BusinessUnitId);
            Assert.Equal(context.CompanyNumber, result.Context.CompanyNumber);
            Assert.True(result.Context.IsGop);
        }
code:
   public async Task<ItemStackResponse> GetItemStackDetail(ItemStackRequest request)
        {
            var salesOrder = await _salesOrderService.GetSalesOrderAsync(request.SalesOrderId);

            return _itemStackBuilder.Build(salesOrder, request);
        }
---------
  private async Task<bool> IsEnableMultishipmentOperationSalesOrderEndpoint()
  {
      var featureToggles = await _featureTogglesService.GetFeatureTogglesAsync();
      return isEnableMultishipmentOperationSalesOrderEndpoint = featureToggles != null && featureToggles.EnableMultishipmentOperationSalesOrderEndpoint;
  }
     public async Task<bool> DeleteShipment(string salesOrderId, string shipmentId)
        {
            await IsEnableMultishipmentOperationSalesOrderEndpoint();
            if (isEnableMultishipmentOperationSalesOrderEndpoint)
            {
                SalesOrderMultishipmentOperationDetail dcqoSalesOrderMultiShipmentRequest = new SalesOrderMultishipmentOperationDetail();
                dcqoSalesOrderMultiShipmentRequest.ResourceId = salesOrderId;
                dcqoSalesOrderMultiShipmentRequest.OperationType= PatchOperationType.Remove;
                salesOrderMultishipmentOperationList?.Add(dcqoSalesOrderMultiShipmentRequest);
                return true;
            }
            else
            {
                return await _salesOrderServiceRepository.DeleteShipment(salesOrderId, shipmentId);
            }
        }
--
        public bool IsQuoteEligibleForSameShipment(QuoteShipment shipment, List<ItemSnapshotDetail> itemSnapshotDetails, List<OutputItem> outputItems, string selectedShippingChoice)
        {
            if (itemSnapshotDetails.IsNullOrEmpty())
            {
                throw new ArgumentNullException(nameof(itemSnapshotDetails));
            }
            var shipment_itemSnapshot = itemSnapshotDetails.Where(item => shipment.Items.Any(shipmentItem => (shipmentItem.QuoteItemId.EqualsOrdinalIgnoreCase(item.QuoteItemId)))).ToList();
            return !outputItems.IsNullOrEmpty() && shipment_itemSnapshot.All(item => outputItems.FirstOrDefault(opItem => opItem.ItemId == item.ItemId)?
                                                                                                .ShippingOptions.Any(op => op.OptionId.EqualsOrdinalIgnoreCase(selectedShippingChoice)) == true);
        }


--
 public bool QuoteShipmentExist(ShippingChargeRequest pricingServiceRequest, QuoteShippingMethodRequest shippingMethodRequest)
        {
            if (pricingServiceRequest == null)
            {
                throw new ArgumentNullException(nameof(pricingServiceRequest));
            }
            if (shippingMethodRequest == null)
            {
                throw new ArgumentNullException(nameof(shippingMethodRequest));
            }
            return pricingServiceRequest.Shipments != null && pricingServiceRequest.Shipments.Any() &&
                   (string.IsNullOrEmpty(pricingServiceRequest?.Shipments.FirstOrDefault()?.ShippingAddress?.PostCode) ||
                   ShipmentHelper.IsPostalCodeMatching(pricingServiceRequest?.Shipments.FirstOrDefault()?.ShippingAddress?.PostCode,
                    shippingMethodRequest.ShippingInfo?.PostalCode));
        }
--
  public List<ShipmentDetails> CreateQuoteShipmentDetails(ShippingChargeRequest pricingServiceRequest, FulfillmentChoiceResponse fulfillmentChoiceResponse, QuoteShippingMethodRequest shippingMethodRequest)
        {
            var shipments = new List<ShipmentDetails>();
            if (pricingServiceRequest == null)
            {
                throw new ArgumentNullException(nameof(pricingServiceRequest));
            }
            if (fulfillmentChoiceResponse == null)
            {
                throw new ArgumentNullException(nameof(fulfillmentChoiceResponse));
            }
            if (shippingMethodRequest == null)
            {
                throw new ArgumentNullException(nameof(shippingMethodRequest));
            }
            var items = pricingServiceRequest.ConfigItems.Where(item => item.IsTied != true).Select(item => new Models.Pricing.ShipmentItem { Id = item.Id, ParentItemId = item.ParentItemId, Quantity = item.Quantity, Weight = item.Weight }).ToList();
            items.AddRange(pricingServiceRequest.SnAItems.Where(item => item.IsTied != true).Select(item => new Models.Pricing.ShipmentItem { Id = item.Id, ParentItemId = item.ParentItemId, Quantity = item.Quantity, Weight = item.Weight }).ToList());
            var shippingChoice = fulfillmentChoiceResponse.OutputItems?.FirstOrDefault()?.ShippingOptions.FirstOrDefault(p => p.IsDefault)?.OptionId ??
                                             _storeSettingsService.GetDefaultStoreShipMethod(shippingMethodRequest.Context).Result;
            var shippingAddress = new ShippingAddress { Country = shippingMethodRequest.ShippingInfo?.Country, PostCode = shippingMethodRequest.ShippingInfo?.PostalCode };
            var shippingOptionIds = fulfillmentChoiceResponse.OutputItems?.SelectMany(x => x.ShippingOptions).Select(x => x.OptionId).Distinct().ToList();
            var parentItems = items.Where(x => string.IsNullOrEmpty(x.ParentItemId) || Guid.Parse(x.ParentItemId) == Guid.Empty);
            var readyStockParentItems = items?.FindAll(x => shippingMethodRequest.ItemSnapshotDetails?.FirstOrDefault(i => i.ItemId == x.Id)?.IsPickOrder ?? false);
            var shipmentDetails = new ShipmentDetails
            {
                ShipmentGroups = new List<ShipmentGroup>(),
                Id = Guid.NewGuid().ToString(),
                ShippingChoice = shippingChoice,
                ShippingAddress = shippingAddress,
                ShippingOptionIds = shippingOptionIds
            };
            foreach (var item in parentItems.Where(x => !readyStockParentItems.Any(i => i.Id == x.Id)))
            {
                var parentChildItems = GetParentIdHierarchy(items, item.Id);
                parentChildItems?.Add(item);
                shipmentDetails.ShipmentGroups.Add(new ShipmentGroup
                {
                    Id = Guid.NewGuid().ToString(),
                    ShipmentUnits = parentChildItems?.Select(x => new ShipmentUnit
                    {
                        ItemId = x.Id,
                        Quantity = Convert.ToInt32(x.Quantity),
                        Weight = x.Weight != null ? (double)x.Weight : 0.0
                    }).ToList()
                });
            }
            shipments.Add(shipmentDetails);
            if (!readyStockParentItems.Any()) return shipments;
            readyStockParentItems.ForEach(item =>
            {
                var parentChildItems = GetParentIdHierarchy(items, item.Id);
                parentChildItems?.Add(item);
                shipments.Add(new ShipmentDetails
                {
                    Id = Guid.NewGuid().ToString(),
                    ShippingChoice = shippingChoice,
                    ShippingAddress = shippingAddress,
                    ShippingOptionIds = shippingOptionIds,
                    ShipmentGroups = new List<ShipmentGroup>
                    {
                        new ShipmentGroup
                        {
                            Id = Guid.NewGuid().ToString(),
                            ShipmentUnits = parentChildItems?.Select(x => new ShipmentUnit
                            {
                                ItemId = x.Id,
                                Quantity = Convert.ToInt32(x.Quantity),
                                Weight = x.Weight != null ? (double)x.Weight : 0.0
                            }).ToList()
                        }
                    }
                });
            });
            return shipments;
        }
