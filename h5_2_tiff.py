# coding:utf-8
import numpy as np
import gdal, ogr, os, osr
import h5py
import math
import os, sys

#タイル番号、画素の位置に対応する緯度経度のメッシュを返す関数
#4800x4800ピクセルすべての緯度経度を求めても遅い＆gdal_translateでエラーになるので100ピクセル毎に間引き
#四隅が欲しいのでgcpの配列の大きさは縦横+1してある
def get_geomesh(filename):
        #タイル縦方向の画素数
        col_tile=4800
        #タイル横方向の画素数
        lin_tile=4800
       
        #グラニュールIDからタイルのIDを取得する
        v_tile=int(input_fine_name[21:23])
        h_tile=int(input_fine_name[23:25])
    
        #SGLI/L2なら固定だと思う
        v_tile_num=18
        h_tile_num=36
        
        #南極から北極までの総画素数
        NL_0=86400
        #赤道における東西方向の総画素数
        NP_0=172800
		#タイルでのメッシュの細かさ
        d=180.0/lin_tile/v_tile_num

   		#gdal_translateに与えるGCPのリスト
		#[x,y,z,経度,緯度]の順番で入れる
        gcp_list=[]
		
        for lin in range(0,lin_tile+1,50):
            for col in range(0,col_tile+1,50):
                if(lin==lin_tile):
                    lin=lin-1
                if(col==col_tile):
                    col=col-1
                lin_total=lin+v_tile*lin_tile
                col_total=col+h_tile*col_tile
                lat=90.0-(lin_total+0.5)*d
                NP_i=NP_0*math.cos(math.radians(lat))
                lon=360.0*(col_total+0.5-NP_0/2)/NP_i
                gcp=gdal.GCP(round(lon,6),round(lat,6),0,col,lin)
                gcp_list.append(gcp)

        return gcp_list
 
if __name__ == '__main__':

	input_file_path="../"
	input_fine_name="GC1SG1_20200701D01D_T0520_L2SG_VGI_Q_2000.h5"
	band_name='NDVI'
	
	output_file_path="./"
	output_filename="tmp.tif"
	output_file=output_file_path+output_filename


	#ファイルを開く
	input_file=input_file_path+input_fine_name
	hdf_file = h5py.File(input_file, 'r')
	print(hdf_file['Image_data'][band_name])
	print(hdf_file['Image_data'][band_name].attrs['Slope'])
	print(hdf_file['Image_data'][band_name].attrs['Offset'])
	print(hdf_file['Image_data'][band_name].attrs['Minimum_valid_DN'])
	print(hdf_file['Image_data'][band_name].attrs['Maximum_valid_DN'])
	print(hdf_file['Image_data'][band_name].attrs['Error_DN'])
	
	#L2のHDF5ファイルのImage_data以下にデータが入っている。
	Image_var=hdf_file['Image_data'][band_name]
	Slope=hdf_file['Image_data'][band_name].attrs['Slope']
	Offset=hdf_file['Image_data'][band_name].attrs['Offset']
	Max_DN=hdf_file['Image_data'][band_name].attrs['Maximum_valid_DN']
	
	#型変換とエラー値をnanに変換する
	Image_var=np.array(Image_var,dtype='uint16')
	Image_var=np.where(Image_var>Max_DN,np.nan,Image_var)


	#GCPのリストをつくる
	gcp_list=get_geomesh(input_fine_name)

	#出力
	dtype = gdal.GDT_UInt16 #others: gdal.GDT_Byte, ...
	band=1
	output = gdal.GetDriverByName('GTiff').Create(output_file,4800,4800,band,dtype) # 空の出力ファイル
	output.GetRasterBand(1).WriteArray(Image_var)
	wkt = output.GetProjection()
	output.SetGCPs(gcp_list,wkt)
	#EPSG4326に投影変換
	output = gdal.Warp(output_file, output, dstSRS='EPSG:4326',outputType=gdal.GDT_Int16)
	output.FlushCache()# ディスクに書き出し
	output = None 	

	hdf_file.close()
