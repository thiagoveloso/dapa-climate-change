#------------------------------------------------------------------------------------------------------------------------------------------------------
# Description: Cut ASCII files from PRECIS in daily data and convert to GRID
# Author: 	   Carlos Navarro, Edward Guevara
# Date:  	   27/09/10
# Notes: 	   - Equivalences standar diagnostic variables are available in trunk\dapa-climate-change\PRECIS\Metereological_Variables.txt
# 		       - If an error ocurs, sup month folder and review and descompress input files if is necessary
#		       - Structure of daily data is   outputdir\monthly_grids\YYYY\Variable\Variable_MM\Variable_MMDD
# 		       - Structure of monthly data is   outputdir\monthly_grids\YYYY\Variable\Variable_MM
# 		       - Use "ConvertAscii2Grid_v1.py" for HadCM3Q3; for other scenarios use "ConvertAscii2Grid.py"
# -----------------------------------------------------------------------------------------------------------------------------------------------------

# Import system modules
import os, arcgisscripting, sys, glob, string, shutil

if len(sys.argv) < 6:
	os.system('clear')
	print "\n Too few args"
	print "   - Sintaxis: "
	print "   - python ConvertAscii2Grid.py D:\climate_change\RCM_Data\SRES_A1B\HadCM3Q0 1959 1959 daily D:\climate_change\RCM_Data\SRES_A1B\HadCM3Q0"
	sys.exit(1)

# Arguments
dirbase = sys.argv[1]
inityear = int(sys.argv[2])
finalyear = int(sys.argv[3])
type = sys.argv[4]
dirout = sys.argv[5]
	
# Dictionary with Standar diagnostic variables
decVar = {"00001": "SurPress", "00024": "TSmean", "00024.max": "TSmax", "00024.min": "TSmin", "02204": "CloudAm", "03234": "SLHeat", "03236": "Tmean1_5", 
		 "03236.max": "Tmax1_5", "03236.min": "Tmin1_5", "03237": "SHum1_5", "03245": "RHum1_5", "03249": "Wsmean", "03249.max": "Wsmax", "03296": "EvSS", 
		 "03297": "EvCR", "03298": "SubSR", "03299": "TransR", "03312": "EvPotR", "03313": "SoilMAF", "03510": "EvPotF1", "03511": "EvPotF2", 
		 "05216": "Prec", "08208": "SoilMRZ", "08225": "TSoil", "16222": "Press", "00024.mmax": "TSmmax", "08223": "SoilML", "16204": "RHum",
		 "00024.mmin": "TSmmin", "03236.mmax": "Tmmax1_5", "03236.mmin": "Tmmin1_5", "03249.mmax": "Wsmmax"} 

os.system('cls')

print "\n"
print "    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print "                         SPLIT ASCIIS PRECIS                       "
print "    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print "\n"

gp = arcgisscripting.create(9.3)

if type == "daily":

	for year in range(inityear, finalyear + 1, 1):
    
		# Set workspace
		gp.workspace = dirbase + "\\" + type + "_asciis\\" + str(year)
		if os.path.exists(gp.workspace):
			print "  > Processing " + gp.workspace + "\n"
			
			# Get a list of asciis in workspace
			ascList = glob.glob(gp.workspace + "\\*.asc")
			for asc in ascList:
				
				# Extact variable of the file name
				variable = os.path.basename(asc).split("_")[0:1][0]
				month = os.path.basename(asc).split("_")[-1][0:2]
				
				if not gp.Exists(dirout + "\\" + type + "_grids\\" + str(year) + "\\Ascii2Grid_" + str(decVar [variable]) + "_done.txt") and not str(variable) == "08223" and not str(variable) == "08225" and not str(variable) == "16204":
					
					print "\n         Processing " + str(decVar[variable]) + "\t" + str(year) + "\t" + str(month)
					
					# Create outputfolder to Grid files
					diroutGrid = dirout + "\\" + type + "_grids\\" + str(year) + "\\" + str(decVar [variable]) + "\\" + str(decVar [variable]) + "_" + str(month)
					if not os.path.exists(diroutGrid):
						#shutil.rmtree(diroutGrid)
						os.system('mkdir ' + diroutGrid)
					#else:
						#os.system('mkdir ' + diroutGrid)
							
					# Split into daily files
					print "         Spliting into daily files and converting to grids"

					if str(variable) == "03249" or str(variable) == "03249.max" or str(variable) == "03249.mmax":
						splitLen = 127
					else:
						splitLen = 128 

					input = open(asc, "r").read().split("\n")

					at = 1
				
					for lines in range(0, len(input), splitLen):

						# Get the list slice
						outputData = input[lines:lines+splitLen]

						# Now open a temporal text file, join the new slice with newlines and write it out. Then close the file.
						if at < 10:
							baseName = str(decVar [variable]) + "_" + str(month) + "0" + str(at)
						else:
							baseName = str(decVar [variable]) + "_" + str(month) + str(at)
						
						tmpTXT = open(gp.workspace + "\\" + baseName + ".txt", "w")
						tmpTXT.write("\n".join(outputData))
						tmpTXT.close()
						
						outASC = open(gp.workspace + "\\" + baseName + ".asc", "w")
						outASC.write("NCOLS 140\nNROWS " + str(int(splitLen)-2) + "\nXLLCORNER -95.48999786377\nYLLCORNER -34.0599986314773\nCELLSIZE 0.439999997615814\nNODATA_VALUE -1073741824\n")
						outASC.close()
						
						tmpTXT = open(gp.workspace + "\\" + baseName + ".txt", "r")
						tmpTXT.readline()
						tmpTXT.readline()

						outASC = open(gp.workspace + "\\" + baseName + ".asc", "a")

						for line in tmpTXT.readlines():
							outASC.write(line)

						tmpTXT.close()
						outASC.close()
						
						os.system("del " + gp.workspace + "\\" + baseName + ".txt")
						
						# Convert ASCII to Raster
						
						if at <> 31:
							InAsc = gp.workspace + "\\" + baseName + ".asc"
							OutGrid = diroutGrid + "\\" + baseName
							gp.ASCIIToRaster_conversion(InAsc, OutGrid, "FLOAT")
							
							InZip = gp.workspace + "\\" + str(decVar [variable]) + "_" + str(year) + str(month) + ".zip"
							os.system("7za a " + InZip + " " + InAsc)
							os.system("del " + InAsc)
							
						else:
							os.system("del " + gp.workspace + "\\" + str(decVar [variable]) + "_" + str(month) + "31.asc")
							
						#Increase Counter
						at += 1
					
					if str(month) == "12":
						#Create check file
						checkTXT = open(dirout + "\\" + type + "_grids\\" + str(year) + "\\Ascii2Grid_" + str(decVar [variable]) + "_done.txt", "w")
						checkTXT.close()
				
					print "         Done!\n"
				
				else:
					print "         Processed " + str(decVar[variable]) + "\t" + str(year) + "\t" + str(month)
					
			
			for asc in ascList:
				# Compress input files
				InZipCom = gp.workspace + "\\_Compiled_asciis.zip"
				os.system("7za a " + InZipCom + " " + asc)
				os.system("del " + asc)
					
if type == "monthly":

	for year in range(inityear, finalyear + 1, 1):
    
		# Set workspace
		gp.workspace = dirbase + "\\" + type + "_asciis\\" + str(year)
		if os.path.exists(gp.workspace):
			print "  > Processing " + gp.workspace + "\n"
			
			# Get a list of asciis in workspace
			ascList = glob.glob(gp.workspace + "\\*.asc")
			for asc in ascList:
				print asc
				# Extact variable of the file name
				variable = os.path.basename(asc).split("_")[0:1][0]
				month = os.path.basename(asc).split("_")[-1][0:2]
				
				if not gp.Exists(dirout + "\\" + type + "_grids\\" + str(year) + "\\Ascii2Grid_" + str(decVar [variable]) + "_done.txt") and not str(variable) == "08223" and not str(variable) == "08225" and not str(variable) == "16204":
					
					print "\n         Processing " + str(decVar[variable]) + "\t" + str(year) + "\t" + str(month)
					
					# Create outputfolder to Grid files
					diroutGrid = dirout + "\\" + type + "_grids\\" + str(year) + "\\" + str(decVar [variable]) 
					if not os.path.exists(diroutGrid):
						# shutil.rmtree(diroutGrid)
						os.system('mkdir ' + diroutGrid)
					# else:
						# os.system('mkdir ' + diroutGrid)
							
					if str(variable) == "03249" or str(variable) == "03249.max" or str(variable) == "03249.mmax":
						splitLen = 127
					else:
						splitLen = 128 
					
					input = open(asc, "r").read().split("\n")

					for lines in range(0, splitLen, splitLen):

						# Get the list slice
						outputData = input[lines:lines+splitLen]

						# Now open a temporal text file, join the new slice with newlines and write it out. Then close the file.
						
						baseName = str(decVar [variable]) + "_" + str(month)
						
						tmpTXT = open(gp.workspace + "\\" + baseName + ".txt", "w")
						tmpTXT.write("\n".join(outputData))
						tmpTXT.close()
						
						outASC = open(gp.workspace + "\\" + baseName + ".asc", "w")					
						outASC.write("NCOLS 140\nNROWS " + str(int(splitLen)-2) + "\nXLLCORNER -95.48999786377\nYLLCORNER -34.0599986314773\nCELLSIZE 0.439999997615814\nNODATA_VALUE -1073741824\n")
						outASC.close()
						
						tmpTXT = open(gp.workspace + "\\" + baseName + ".txt", "r")
						tmpTXT.readline()
						tmpTXT.readline()

						outASC = open(gp.workspace + "\\" + baseName + ".asc", "a")

						for line in tmpTXT.readlines():
							outASC.write(line)

						tmpTXT.close()
						outASC.close()
						
						os.system("del " + gp.workspace + "\\" + baseName + ".txt")
						
						# Convert ASCII to Raster
						InAsc = gp.workspace + "\\" + baseName + ".asc"
						OutGrid = diroutGrid + "\\" + baseName
						gp.ASCIIToRaster_conversion(InAsc, OutGrid, "FLOAT")
						
						InZip = gp.workspace + "\\" + str(decVar [variable]) + "_" + str(year) + ".zip"
						os.system("7za a " + InZip + " " + InAsc)
						os.system("del " + InAsc)
							

					if str(month) == "12":
						#Create check file
						checkTXT = open(dirout + "\\" + type + "_grids\\" + str(year) + "\\Ascii2Grid_" + str(decVar [variable]) + "_done.txt", "w")
						checkTXT.close()
				
					print "         Done!\n"
				
				else:
					print "         Processed " + str(decVar[variable]) + "\t" + str(year) + "\t" + str(month)
					
			
			for asc in ascList:
				# Compress input files
				InZipCom = gp.workspace + "\\_Compiled_asciis.zip"
				os.system("7za a " + InZipCom + " " + asc)
				os.system("del " + asc)
				
print "  > Process done!!!"