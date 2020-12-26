# coding:utf-8
import numpy as np
import gdal, ogr, os, osr,sys
import gdalconst
import h5py
import math

#タイル番号、画素の位置に対応する緯度経度のメッシュを返す関数
#4800x4800ピクセルすべての緯度経度を求めても遅い＆gdal_translateでエラーになるので間引き
#四隅が欲しいのでgcpの配列の大きさは縦横+1してある
def get_geomesh(filename,lintile,coltile):

	#グラニュールIDからタイル番号を取得する
	#縦方向
	vtile=int(input_file_name[21:23])
	#横方向
	htile=int(input_file_name[23:25])
   
	#SGLI/L2であれば固定
	#縦方向の総タイル数
	vtilenum=18
	#横方向の総タイル数
	htilenum=36
		
	#緯度方向(dlin)、経度方向(dcol)
	#それぞれの1画素の大きさ
	#d=dlin=dcol
	d=180.0/lintile/vtilenum
		
	#求めたりタイル番号の左上画素の中心の緯度[deg]は、
	#1タイルあたりの角度が10[deg]であることから、
	lat0=90.0-vtile*10-d/2

	#求めたいタイル番号の左上画素の中心の経度[deg]は、
	#1タイルあたりの角度が10[deg]であることから、
	lon0=-180.0+htile*10+d/2

	#gdal_translateに与えるGCPのリスト
	gcp_list=[]

	for lin in range(0,lintile+1,100):
		lat=lat0-lin*d
		r=np.cos(np.radians(lat))
		for col in range(0,coltile+1,100):
			if(lin==lintile):
				lin=lin-1
			if(col==coltile):
				col=col-1
			lon=(lon0+col*d)/r
			gcp=gdal.GCP(round(lon,6),round(lat,6),0,col+0.5,lin+0.5)
			gcp_list.append(gcp)

	return gcp_list
 
if __name__ == '__main__':

#入力するファイルの情報#
	#ファイル名
	input_file=sys.argv[1]
	#バンド名
	band_name=sys.argv[2]

#出力ファイル名
	output_file=sys.argv[3]


	try:
		hdf_file = h5py.File(input_file, 'r')
	except:
		print('%s IS MISSING.' % input_file)
		exit(1);
	
	hdf_file = h5py.File(input_file, 'r')

	print('OPEN %s.' % input_file)

	#L2のHDF5ファイルのImage_data以下にデータが入っている。
	try:
		Image_var=hdf_file['Image_data'][band_name]
	except:
		print('%s IS MISSING.' % band_name)
		print('SELECT FROM')
		print(hdf_file['Image_data'].keys())
		exit(1);

	input_file_name=str(hdf_file['Global_attributes'].attrs['Product_file_name'][0][2:45])
	#L2のHDF5ファイルのImage_data以下にデータが入っている。
	Image_var=hdf_file['Image_data'][band_name]
	Slope=hdf_file['Image_data'][band_name].attrs['Slope']
	Offset=hdf_file['Image_data'][band_name].attrs['Offset']
	Max_DN=hdf_file['Image_data'][band_name].attrs['Maximum_valid_DN']
	Min_DN=hdf_file['Image_data'][band_name].attrs['Minimum_valid_DN']
	
	#型変換とエラー値をnanに変換する
	Image_var=np.array(Image_var,dtype='uint16')
	Image_var=np.where(Image_var>Max_DN,np.nan,Image_var)

	#値を求める
	Value_arr=Slope*Image_var+Offset
	Value_arr=np.array(Value_arr,dtype='float32')

	#行数
	lin_size=Image_var.shape[0]
	#列数
	col_size=Image_var.shape[1]

	#GCPのリストをつくる
	gcp_list=get_geomesh(input_file_name,lin_size,col_size)

	#出力
	dtype = gdal.GDT_Float32
	band=1
	output = gdal.GetDriverByName('GTiff').Create(output_file,lin_size,col_size,band,dtype) 
	output.GetRasterBand(1).WriteArray(Value_arr)
	wkt = output.GetProjection()
	output.SetGCPs(gcp_list,wkt)
	#与えたGCPを使ってEPSG4326に投影変換
	output = gdal.Warp(output_file, output, dstSRS='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',srcNodata=np.nan,dstNodata=np.nan,tps = True, outputType=dtype,multithread=True,resampleAlg=gdalconst.GRIORA_NearestNeighbour)
	output.FlushCache()
	output = None 	

	hdf_file.close()
