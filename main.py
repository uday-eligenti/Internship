from flask import *

app=Flask(__name__)

@app.route('/',methods=['POST','GET'])
def home():
    file_name=''
    start_line=''
    end_line=''
    en="utf-8"
    if request.method=='GET':
        file_name=request.args.get('file_name')
        start_line=request.args.get('start_line')
        end_line=request.args.get('end_line')
        #print(file_name,start_line,end_line)       
        if file_name=='' or file_name==None:
            file_name='file1.txt'
        if (start_line=='' and end_line=='') or (start_line==None and end_line==None):
            try:
                print(file_name)
                if file_name=='file4.txt':
                    en='utf-16'
                    
                with open(str(file_name),'r',encoding=en, errors='ignore') as x:
                    data=x.readlines()
                    return render_template('index.html',file=data,n=file_name)
            except:
                return 'File Not found!! Please enter a valid file name..'
        else:
        	try:
        		if file_name=='file4':
        			en='utf-16'
        		with open(str(file_name),'r',encoding=en, errors='ignore') as x:
        			
        			arr=x.readlines()
        			data=[]
        			print("--------",len(arr))
        			if (start_line=='' and end_line!=''):
        				start_line=0
        			if (start_line!='' and end_line=='') or (start_line!=None and end_line==None):
        				end_line=len(arr)
        				#end_line=str(l)
        			for i in range(int(start_line),int(end_line)):
        				print(start_line)
        				data.append(arr[i])
        			return render_template('index.html',file=data,n=file_name)
                    
        	
        	except FileNotFoundError:
        		return 'File Not found!! Please enter a valid file name..'
        	except:
        		return 'Invalid input detected.. Please enter a valid input..'
if __name__ == "__main__":
	app.run(debug=True)