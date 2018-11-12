#python eventdetection_tw.py -datadir ../ni_data/process_events2012/ -psfile ../ni_data/process_events2012/frmps > log.ed_k5t2_match2
#python eventdetection_tw.py -datadir ../ni_data/process_events2012/ -psfile ../ni_data/process_events2012/frmps -k 10 > log.ed_k10t2_m2
#python eventdetection_tw.py -datadir ../ni_data/process_events2012/ -eval > log.ed_k5t2_match1

#python eventdetection_tw.py -datadir ../ni_data/process_events2012/ -eval > log.ed_k5t2_m2
#python eventdetection_tw.py -datadir ../ni_data/process_events2012/ -eval -t 5 > log.ed_k5t5_m2
python eventdetection_tw.py -datadir ../ni_data/process_events2012/ -eval -t 10 > log.ed_k5t10_m2 &
#python eventdetection_tw.py -datadir ../ni_data/process_events2012/ -eval -k 10 > log.ed_k10t2_m2 &
#python eventdetection_tw.py -datadir ../ni_data/process_events2012/ -eval -k 10 -t 5 > log.ed_k10t5_m2
#python eventdetection_tw.py -datadir ../ni_data/process_events2012/ -eval -k 10 -t 10 > log.ed_k10t10_m2
