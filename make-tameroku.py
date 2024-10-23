#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import glob
import json

if sys.platform == 'win32':
    TONAME = '\\\\.\\pipe\\ToSrvPipe'
    FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
else:
    TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
    FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
    EOL = '\n'

TOFILE = open(TONAME, 'w')
FROMFILE = open(FROMNAME, 'rt', encoding="utf8")

def send_command(command):
    TOFILE.write(command + EOL)
    TOFILE.flush()

def get_response():
    result = ''
    line = ''
    while True:
        result += line
        line = FROMFILE.readline()
        if line == '\n' and len(result) > 0:
            break
    return result

def do_command(command):
    print(command)
    send_command(command)
    response = get_response()
    print(response)
    return response

########################

if len(sys.argv) != 4:
    print("invalid argument")
    sys.exit()

#in_folder = "c:\\work\\inajob-podcast\\20240903" # sys.argv[1]
in_folder = sys.argv[1]
change_sound = sys.argv[2]
bgm_sound = sys.argv[3]

files = "*.m4a"
files = glob.glob(os.path.join(in_folder, files))

for file in files:
    print(file)
    do_command('Import2: Filename="' + file + '"')

do_command('SelectAll:')

# TODO: manual operation
# do_command('NoiseReduction:') # get profile
# do_command('NoiseReduction:') # noise reduction
# ノイズ低減は手動で作業が必要なのでスクリプトは一時停止する
input("press any key")

do_command('SelectAll:')
do_command('TruncateSilence: Threshold=-35 Minimum=0.1 Truncate=0.1 Independent=True') # 無音切りつめ
do_command('LoudnessNormalization: LUFSLevel=-14.0') # ラウドネスノーマライズ

# 並べる
for x in range(len(files) - 1):
    # Track 1のクリップを選択して切り取る
    do_command('SelectTracks: Track=1 TrackCount=1')
    do_command('SelPrevClip:')
    do_command('Cut:')
    # Track 1を削除(Track 2があればTrack 1に繰り上がる)
    do_command('RemoveTracks:')
    # Track 0を選択
    do_command('SelectTracks: Track=0 TrackCount=1')
    # 末尾に移動
    do_command('CursTrackEnd:')
    print(x, len(files) - 2)
    if x == len(files) - 2: # last track
        # 最後のクリップだけ4秒後ろにずらして配置
        print("last track")
        do_command('SelectTime: Start=4.0 End=4.0 RelativeTo=SelectionStart')
    # コピーしておいたクリップを貼り付け
    do_command('Paste:')
# 全体を少し右にずらす
do_command('SelectAll:')
do_command('Cut:')
do_command('SelectTime: Start=4.0 End=4.0 RelativeTo=ProjectStart')
do_command('Paste:')

# 効果音を読み込んでクリップボードに入れる
do_command('Import2: Filename="' + change_sound + '"')
do_command('SelectTracks: Track=1 TrackCount=1')
do_command('SelPrevClip:')
do_command('Cut:')

# 一番初めの境界はスキップする
do_command('SelectTracks: Track=0 TrackCount=1')
do_command('CursNextClipBoundary:') 

# 隙間に効果音を入れる
for x in range(len(files)-2):
    do_command('SelectTracks: Track=0 TrackCount=1')
    do_command('CursNextClipBoundary:') 
    do_command('SelectTracks: Track=1 TrackCount=1')
    do_command('Paste:')

# BGMを挿入して音量を調整する
do_command('Import2: Filename="' + bgm_sound + '"')
do_command('SetEnvelope: Time=0 Value=1')
do_command('SetEnvelope: Time=3 Value=1')
do_command('SetEnvelope: Time=6 Value=0.1')
# BGMを後ろでも使うのでコピー
do_command('SelectTracks: Track=2 TrackCount=2')
do_command('SelPrevClip:')
do_command('Copy:')
for x in range(len(files)-2):
    # 最後のClipの手前まで移動
    do_command('SelectTracks: Track=0 TrackCount=1')
    do_command('CursNextClipBoundary:') 
# 最後Clipの先頭から3秒前にBGMを貼り付け
do_command('SelectTracks: Track=2 TrackCount=1')
do_command('SelectTime: Start=1.0 End=1.0 RelativeTo=SelectionStart')
do_command('Paste:')

# 最後のBGMをClipに合わせて切り取る
info = do_command("GetInfo: Type=Clips")
info_obj = json.loads("\n".join(info.split("\n")[:-2]))
print(info_obj)
last_clip = None
last_bgm = None
for c in info_obj:
    if c["track"] == 0:
        last_clip = c
    if c["track"] == 2:
        last_bgm = c
print(last_clip)
print(last_bgm)

# BGMの方がCLIPより長いとき
if(last_clip["end"] + 4 < last_bgm["end"]):
    # 最後のClipとBGMのお尻をあわせる
    do_command('SelectTracks: Track=2 TrackCount=1')
    do_command('SetEnvelope: Time=' + str(last_clip["end"]) + ' Value=0.1')
    do_command('SetEnvelope: Time=' + str(last_clip["end"]+0.5) + ' Value=0.05')
    do_command('SetEnvelope: Time=' + str(last_clip["end"]+1) + ' Value=0')
    do_command('SelectTime: Start=' + str(last_clip["end"]+4) + ' End=' + str(last_bgm["end"]) + '')
    do_command('Delete:')

TOFILE.close()
FROMFILE.close()
