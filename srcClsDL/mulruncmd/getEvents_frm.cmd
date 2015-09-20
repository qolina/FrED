python estimatePs_smldata.py 
#sync
python getbtySkl.py 01 ../parsedTweet/eventskl01_v7loc
#sync
python getbtyFrm.py 01 ../parsedTweet/eventskl01_v7loc ../parsedTweet/eventfrm01_v7loc
#sync
python getEventFrmPair.py 01 ../parsedTweet/eventskl01_v7loc ../parsedTweet/eventfrm01_v7loc ../parsedTweet/segPairFile01_v7loc
#sync
python getEvent.py 01 ../parsedTweet/segPairFile01_v7loc ../parsedTweet/EventFile01_v7loc
#exit
