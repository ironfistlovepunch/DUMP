import sys
import os
import io
import struct
import re
import binascii

import xml.etree.ElementTree as ET
from unicodedata import normalize

def get_pce_filename(alldata,fi):
		#PCEファイル名
		key = b"\x2E\x50\x43\x45" #.PCE (2E 50 43 45)
		pos = alldata.find(key)
			
		j = 0
		list_pcename = []
		while True:
			fi.seek(pos+3-j)
			char_name = fi.read(1)
			print(char_name)
			if char_name < b"\x20" or char_name > b"\x7E":
				#ファイル名じゃなさそう
				break
			list_pcename.append(char_name.decode())
			j = j + 1
			
			if j == 40:
				#とりあえずリミット
				break
				
		list_pcename.reverse()
		#ファイル名を整える
		pcename = "".join(list_pcename).replace(" ","") #スペース取る
		pcename = pcename.replace("'","") #'を取る
		
		print("PCEファイル名")
		print(pcename)
		
		return pcename
	
def main(sourcefile,cutsize):
	#入力ファイル
	filename = os.path.basename(sourcefile)
	filedir = os.path.dirname(sourcefile)
	file_size = os.path.getsize(sourcefile)
	
	print("input")
	print(sourcefile)
	print("filename")
	print(filename)
	print("dir")
	print(filedir)
	print("size")
	print(file_size)

	#元のファイルを開く
	with open(sourcefile, mode='rb') as fi:
		alldata = fi.read()
		fi.seek(0)
		
		#ヘッダーぽいの探す
		print("#ヘッダー")
		i = 0
		offset = 0
		while True:
			i = i + 1
			print(i)

			#検索
			key_pce = b"\x2E\x50\x43\x45" #.PCE (2E 50 43 45)

			pos_pce = alldata.find(key_pce,offset)
			offset = pos_pce + 4
			
			print("pos_pce")
			print(pos_pce)
			print(hex(pos_pce))
			
			#終了判定
			if pos_pce==-1:
				print("おわり")
				break

			#読み込み開始
			fi.seek(pos_pce)
			
			#.PCE
			dot_pce = fi.read(4)
			print(dot_pce)
			#00
			space00 = fi.read(1)
			print("00space")
			print(space00)
			pos_header = fi.tell()
			print(pos_header)
			#ヘッダぽい8バイト
			header = fi.read(8)
			print("HEADER?")
			print(header)
			
			if header != b"\x00\x00\x00\x00\x00\x00\x00\x00":
				#ヘッダーぽいのみつかる
				break
				
		#PCEファイル名
		pcename = get_pce_filename(alldata,fi)

		#本体部分
		print("#ROM")
		i = 0
		offset = 0
		while True:
			i = i + 1
			print()
			print(i)
			
			if i==5:
				#とりあえずリミット
				break
			
			#ヘッダーぽいのを探す
			pos_header = alldata.find(header,offset)
			print(pos_header)

			#次のループ用			
			offset = pos_header + 8
	
			#終了判定
			if pos_header==-1:
				print("おわり")
				break
		
			#出力データ準備
			fi.seek(pos_header)
			out_data = fi.read(cutsize)
			
			#CRC32
			crc32 = binascii.crc32(out_data)
			crc32 = '{:X}'.format(crc32)
			print("CRC32")
			print(crc32)
			
			#.PCEがある場合は除外
			fi.seek(pos_header-5)
			dot_pce = fi.read(4)
			print(dot_pce)

			if dot_pce==key_pce:
				print(".PCEあり")
				continue
				
			#出力ファイル名
			outfile = os.path.splitext(os.path.basename(pcename))[0] + "_" + crc32 + ".PCE"
			#出力
			with open(outfile,mode="wb") as fo:
				fo.write(out_data)

		return 

#プログラム実行
if __name__ == "__main__":
	#ファイル入力
	if len(sys.argv) == 1:
		#指定がない場合
		#sourcefile = "bomberman94.DMP"
		#cutsize = 0x100000

		sourcefile = "takahasimeijin.DMP"
		cutsize = 524288

	else:
		sourcefile = sys.argv[1]
		cutsize = int(sys.argv[2],0)

	#メイン処理
	main(sourcefile,cutsize)
