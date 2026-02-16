
import time
import API_Call
import Parser
import colorParsing

def main():
    print("Calling API_Call module ...\n")

    if API_Call.API_Call()==True:
        print("API call was successful. Calling Parser module ...\n")
        Parser.open_File()
        #colorParsing.main()
        
    else:
        print("API call failed.\n")

if __name__ =="__main__":
    start_time = time.time()
    main()
    print("---- Runtime = %s seconds ----" % (time.time() - start_time))