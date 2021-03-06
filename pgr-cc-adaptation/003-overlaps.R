#Julian Ramirez-Villegas
#Jan 2012

library(raster); library(sfsmisc); library(maptools)

#src.dir <- "~/Repositories/dapa-climate-change/trunk/pgr-cc-adaptation"
src.dir <- "~/PhD-work/_tools/dapa-climate-change/trunk/pgr-cc-adaptation"
source(paste(src.dir,"/pgr-cc-adaptation-functions.R",sep=""))

# #base directories
# gcmDir <- "/mnt/a102/eejarv/CMIP5/Amon"
# bDir <- "/mnt/a17/eejarv/pgr-cc-adaptation"
# scratch <- "~/Workspace/pgr_analogues"

gcmDir <- "/nfs/a102/eejarv/CMIP5/Amon"
bDir <- "/nfs/a17/eejarv/pgr-cc-adaptation"
scratch <- "/scratch/eejarv/pgr_analogues"

#input directories
hisDir <- paste(gcmDir,"/historical_amon",sep="")
rcpDir <- paste(gcmDir,"/rcp45_amon",sep="")
cfgDir <- paste(bDir,"/config",sep="")
cruDir <- paste(bDir,"/cru-data",sep="")
if (!file.exists(scratch)) {dir.create(scratch)}

#output directories
out_bDir <- paste(bDir,"/outputs",sep="")
if (!file.exists(out_bDir)) {dir.create(out_bDir)}

#configuration details and initial data
yi_h <- 1966; yf_h <- 2005
yi_f1 <- 2016; yf_f1 <- 2055
yi_f2 <- 2056; yf_f2 <- 2095
gcmList <- read.csv(paste(cfgDir,"/gcm_list.csv",sep=""))

#area harvested rasters
ha_rs <- list()
ha_rs$RICE <- raster(paste(bDir,"/crop-data/Rice.harea/rice_harea_glo.tif",sep=""))
ha_rs$WSPR <- raster(paste(bDir,"/crop-data/Wheat.harea/wheat_harea_glo.tif",sep=""))
ha_rs$WWIN <- raster(paste(bDir,"/crop-data/Wheat.harea/wheat_harea_glo.tif",sep=""))
ha_rs$MILL <- raster(paste(bDir,"/crop-data/Millet.harea/millet_harea_glo.tif",sep=""))
ha_rs$SORG <- raster(paste(bDir,"/crop-data/Sorghum.harea/sorghum_harea_glo.tif",sep=""))

#sowing and harvest date rasters
ca_rs <- list()
ca_rs$RICE <- list()
ca_rs$RICE$PL <- raster(paste(bDir,"/crop-data/Rice.crop.calendar.fill/plant_month.tif",sep=""))
ca_rs$RICE$HR <- raster(paste(bDir,"/crop-data/Rice.crop.calendar.fill/harvest_month.tif",sep=""))
ca_rs$WSPR <- list()
ca_rs$WSPR$PL <- raster(paste(bDir,"/crop-data/Wheat.crop.calendar.fill/plant_month.tif",sep=""))
ca_rs$WSPR$HR <- raster(paste(bDir,"/crop-data/Wheat.crop.calendar.fill/harvest_month.tif",sep=""))
ca_rs$WWIN <- list()
ca_rs$WWIN$PL <- raster(paste(bDir,"/crop-data/Wheat.Winter.crop.calendar.fill/plant_month.tif",sep=""))
ca_rs$WWIN$HR <- raster(paste(bDir,"/crop-data/Wheat.Winter.crop.calendar.fill/harvest_month.tif",sep=""))
ca_rs$MILL <- list()
ca_rs$MILL$PL <- raster(paste(bDir,"/crop-data/Millet.crop.calendar.fill/plant_month.tif",sep=""))
ca_rs$MILL$HR <- raster(paste(bDir,"/crop-data/Millet.crop.calendar.fill/harvest_month.tif",sep=""))
ca_rs$SORG <- list()
ca_rs$SORG$PL <- raster(paste(bDir,"/crop-data/Sorghum.crop.calendar.fill/plant_month.tif",sep=""))
ca_rs$SORG$HR <- raster(paste(bDir,"/crop-data/Sorghum.crop.calendar.fill/harvest_month.tif",sep=""))

#cru raster to filter out NAs
dum_rs <- raster(paste(cruDir,"/cru_ts_3_10.1966.2005.tmx.dat.nc",sep=""),band=0)

#data.frame of grid cells to extract
gCells <- data.frame(LOC=which(!is.na(dum_rs[])))
gCells$LON <- xFromCell(dum_rs,gCells$LOC)
gCells$LAT <- yFromCell(dum_rs,gCells$LOC)
gCells$RICE <- extract(ha_rs$RICE,cbind(x=gCells$LON,y=gCells$LAT))
gCells$RICE[which(!is.na(gCells$RICE))] <- 1
gCells$RICE[which(is.na(gCells$RICE))] <- 0
gCells$WSPR <- extract(ha_rs$WSPR,cbind(x=gCells$LON,y=gCells$LAT))
gCells$WSPR[which(!is.na(gCells$WSPR))] <- 1
gCells$WSPR[which(is.na(gCells$WSPR))] <- 0
gCells$WWIN <- extract(ha_rs$WWIN,cbind(x=gCells$LON,y=gCells$LAT))
gCells$WWIN[which(!is.na(gCells$WWIN))] <- 1
gCells$WWIN[which(is.na(gCells$WWIN))] <- 0
gCells$MILL <- extract(ha_rs$MILL,cbind(x=gCells$LON,y=gCells$LAT))
gCells$MILL[which(!is.na(gCells$MILL))] <- 1
gCells$MILL[which(is.na(gCells$MILL))] <- 0
gCells$SORG <- extract(ha_rs$SORG,cbind(x=gCells$LON,y=gCells$LAT))
gCells$SORG[which(!is.na(gCells$SORG))] <- 1
gCells$SORG[which(is.na(gCells$SORG))] <- 0
gCells$TOTL <- gCells$RICE+gCells$WSPR+gCells$WWIN+gCells$MILL+gCells$SORG
gCells <- gCells[which(gCells$TOTL > 0),]
row.names(gCells) <- 1:nrow(gCells)

#gcm
#gcm_i <- 1 #16 is HadGEM2-AO #22 is MIROC5 #17 is HadGEM2-CC
#batch 1 --> c(1,16,22,17)
#batch 2 --> c(2:15,17:21,23)
for (gcm_i in c(1:6,9,16,19,22)) {
  gcm <- paste(gcmList$GCM[gcm_i])
  ens <- paste(gcmList$ENS[gcm_i])
  
  #output GCM-specific directory
  gcm_outDir <- paste(out_bDir,"/",gcmList$GCM_ENS[gcm_i],sep="")
  if (!file.exists(gcm_outDir)) {dir.create(gcm_outDir)}
  
  #check existence
  gCells$STATUS <- sapply(as.numeric(row.names(gCells)),check_done)
  gCells_u <- gCells[which(!gCells$STATUS),]
  analyse_gridcell(as.numeric(row.names(gCells_u))[1])
  
  ####################################################################
  ####################################################################
  #number of cpus to use
  if (nrow(gCells_u) > 15) {ncpus <- 15} else {ncpus <- nrow(gCells)}
  
  #here do the parallelisation
  #load library and create cluster
  library(snowfall)
  sfInit(parallel=T,cpus=ncpus)
  
  #export variables
  sfExport("src.dir")
  sfExport("gcmDir")
  sfExport("bDir")
  sfExport("scratch")
  sfExport("hisDir")
  sfExport("rcpDir")
  sfExport("cfgDir")
  sfExport("cruDir")
  sfExport("out_bDir")
  sfExport("yi_h")
  sfExport("yf_h")
  sfExport("yi_f1")
  sfExport("yf_f1")
  sfExport("yi_f2")
  sfExport("yf_f2")
  sfExport("gcmList")
  sfExport("ha_rs")
  sfExport("ca_rs")
  sfExport("gCells")
  sfExport("gCells_u")
  sfExport("gcm_i")
  sfExport("gcm")
  sfExport("ens")
  sfExport("gcm_outDir")
  
  #sets of runs
  #run the function in parallel
  system.time(sfSapply(as.vector(as.numeric(row.names(gCells_u))),analyse_gridcell))
  
  #stop the cluster
  sfStop()
}



