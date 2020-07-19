# coding:utf-8
import numpy as np
import h5py
import math
#from mpl_toolkits.basemap import Basemap
import os, sys
import tifffile
#from skimage import io

#自作の四捨五入関数
def my_round_func(input_var):
	tmp=int(input_var*10)
	if(tmp%10<5):
		return int(input_var)
	else:
		return int(input_var)+int(1)

#タイル番号、画素の位置に対応する緯度経度のメッシュを返す関数
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

        d=180.0/lin_tile/v_tile_num

        #nanで初期化
        #latlon_mesh[col_tile,lin_tile,0]=lat
        #latlon_mesh[col_tile,lin_tile,1]=lon
        #とする
        latlon_mesh=np.empty((col_tile+1,lin_tile+1,2))
        for lin in range(0,lin_tile+1,1):
            for col in range(0,col_tile+1,1):

                lin_total=lin+v_tile*lin_tile
                col_total=col+h_tile*col_tile
#                lat=90.0-(lin_total+0.5)*d
                lat=90.0-(lin_total)*d
#                NP_i=round(NP_0*math.cos(math.radians(lat)))
                NP_i=NP_0*math.cos(math.radians(lat))
#                lon=360.0/NP_i*(col_total-NP_0/2+0.5)
                lon=360.0*(col_total-NP_0/2)/NP_i
                latlon_mesh[lin,col,0]=round(lat,6)
                latlon_mesh[lin,col,1]=round(lon,6)

        return latlon_mesh
 
if __name__ == '__main__':

    input_file_path="./"
    input_fine_name="GC1SG1_20200701D01D_T0520_L2SG_VGI_Q_2000.h5"
    input_file=input_file_path+input_fine_name
    #ファイルを開く
    hdf_file = h5py.File(input_file, 'r')

    band_name='NDVI'
    print(hdf_file['Geometry_data'].attrs['Upper_left_latitude'],\
			hdf_file['Geometry_data'].attrs['Upper_left_longitude'])
    print(hdf_file['Geometry_data'].attrs['Upper_right_latitude'],\
			hdf_file['Geometry_data'].attrs['Upper_right_longitude'])
    print(hdf_file['Geometry_data'].attrs['Lower_left_latitude'],\
			hdf_file['Geometry_data'].attrs['Lower_left_longitude'])
    print(hdf_file['Geometry_data'].attrs['Lower_right_latitude'],\
			hdf_file['Geometry_data'].attrs['Lower_right_longitude'])

    print(hdf_file['Image_data'][band_name])
#    print(hdf_file['Image_data'][band_name].attrs['Slope'])
#    print(hdf_file['Image_data'][band_name].attrs['Offset'])
#    print(hdf_file['Image_data'][band_name].attrs['Minimum_valid_DN'])
#    print(hdf_file['Image_data'][band_name].attrs['Maximum_valid_DN'])
#    print(hdf_file['Image_data'][band_name].attrs['Error_DN'])
#    #取り出したいところを取り出す。
#    #L2のHDF5ファイルのImage_data以下にデータが入っている。
#    #複数のデータがあるらしいから、欲しいもんだけを取り出す。
#    #左上がデータの最初。左下からではないことに注意
#    Image_var=hdf_file['Image_data'][band_name]
#    Slope=hdf_file['Image_data'][band_name].attrs['Slope']
#    Offset=hdf_file['Image_data'][band_name].attrs['Offset']
#    Error_DN=hdf_file['Image_data'][band_name].attrs['Error_DN']
##    #型変換
#    Image_var=np.array(Image_var,dtype='uint16')
#    Image_var=np.where(Image_var==Error_DN,np.nan,Image_var)
#
#    #陸域反射率を求める
#    Rt=Slope*Image_var+Offset
#
#    #開けたら閉める
#    hdf_file.close()
#
#    #タイル横方向の画素数
#    lin_tile=4800
#    #タイル縦方向の画素数
#    col_tile=4800
#
#    output_file_path="./"
#    output_filename=band_name+"_tmp.tif"
#    output_file=output_file_path+output_filename
#    tifffile.imsave(output_file,Rt)
#
#    #緯度経度情報のメモ書きを残す
#    memo="gcp_memo.txt"
#
    latlon_mesh=get_geomesh(input_fine_name)
    print(latlon_mesh[0][0],latlon_mesh[0][-1])
    print(latlon_mesh[-1][0],latlon_mesh[-1][-1])
#    f=open(input_fine_name[0:-3]+memo,'w')
#    for i in range(0,4800,200):
#        for j in range(0,4800,200):
#            f.write("-gcp "+str(j)+" "+str(i)+" "+str(latlon_mesh[i,j][1])+" "+str(latlon_mesh[i,j][0])+"\n")

#    f.close()
    hdf_file.close()
