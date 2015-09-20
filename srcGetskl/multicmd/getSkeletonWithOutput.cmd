python getSkeleton.py ../parsedTweet Tagtext_2013-01-01.ps > ../outputstr/out.getskl01-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-02.ps > ../outputstr/out.getskl02-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-03.ps > ../outputstr/out.getskl03-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-04.ps > ../outputstr/out.getskl04-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-05.ps > ../outputstr/out.getskl05-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-06.ps > ../outputstr/out.getskl06-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-07.ps > ../outputstr/out.getskl07-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-08.ps > ../outputstr/out.getskl08-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-09.ps > ../outputstr/out.getskl09-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-10.ps > ../outputstr/out.getskl10-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-11.ps > ../outputstr/out.getskl11-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-12.ps > ../outputstr/out.getskl12-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-13.ps > ../outputstr/out.getskl13-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-14.ps > ../outputstr/out.getskl14-mod
python getSkeleton.py ../parsedTweet Tagtext_2013-01-15.ps > ../outputstr/out.getskl15-mod
#sync
cat ../outputstr/out.getskl??-mod > ../outputstr/out.getskl-mod
#sync
rm ../outputstr/out.getskl??-mod
#exit
