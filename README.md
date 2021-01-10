# このプログラム?  
JAXA GCOM-C SGLIのLevel2のHDF5ファイルをgeotiffに変換と地図投影するpythonプログラムです。
2020年12月22日公開のGCOM-Cデータ利用ハンドブックで紹介されているL2タイルの緯度経度計算方法を適用しました。
h5pyを使用せずにgdalライブラリでファイル読み込み、処理が完結するように修正しました。
# 環境  
 開発環境は以下です。
* CentOS Linux release 7.7.1908 (Core)
* python 3.7.4
~* h5py 2.9.0~
* hdf5 1.10.4
* numpy 1.16.5
* gdal 1.11.4

# 既知の問題点
~gcpを与えるときに標高を考慮していません。~
~open street mapなどと比較したとき、海岸線は合うと思いますが、標高の高い地域では位置ずれが発生します。~
~SRTMやAW3DなどのDSMから標高データを元に標高データをgcpに与える必要があります。~  
陸域プロダクトは、精密幾何補正を行っています。GCPを用いて高度による視差の補正を行っているので、位置ずれは小さいと思われます。
リサンプリング方法にNearest neighborをしています。
