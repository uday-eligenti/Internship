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
