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
