#!/bin/bash
# A simple script to automate the dumping of existing
# data within the vocab system. The resulting files can
# then be used to load into the system. It also enables
# datetime labelled backups of all data.
#
# It is just wrapper around standard Django commands
# for this project.
#
VDATA='./vdata/fixtures'
VADMIN='./vadmin/fixtures'
DUMP='./manage.py dumpdata --indent 4'
#WHEN=$(date +%F)
WHEN=$(date "+on%F.at%T") #include time

if [ "$1" == "load" ];
then
	echo 'Loading fixture data for certain models.'
	echo 'WARNING   WARNING'
	echo 'Are you sure you wish to replace existing data?'
	echo 'Type LOAD and press enter if you are 100% sure.'
	read OKAY
	if [ "$OKAY" == "LOAD" ];
	then
		./manage.py loaddata "$VDATA/format.json"
		./manage.py loaddata "$VDATA/collection.json"
		./manage.py loaddata "$VDATA/tag.json"
		./manage.py loaddata "$VDATA/category.json"
		./manage.py loaddata "$VADMIN/group.json" #must go before user
		./manage.py loaddata "$VADMIN/user.json"
		./manage.py loaddata "$VADMIN/page.json"
		./manage.py loaddata "$VDATA/document.json" #REPLACE MAIN DOCUMENTS
		echo 'Finished loading, check the admin site is as expected.'
	else
		echo 'Loading cancelled.'
	fi

elif [ "$1" == "dump" ];
then
	echo 'Dumping fixture data for certain models.'
	echo 'WARNING   WARNING'
	echo 'Are you sure you wish to replace the last set of DUMPED data?'
	echo 'Type DUMP and press enter if you are 100% sure.'
	read OKAY
	if [ "$OKAY" == "DUMP" ];
	then	
		$($DUMP vdata.format > "$VDATA/format.json")
		$($DUMP vdata.collection > "$VDATA/collection.json")
		$($DUMP vdata.tag > "$VDATA/tag.json")
		$($DUMP vdata.category > "$VDATA/category.json")
		$($DUMP auth.group > "$VADMIN/group.json")	
		$($DUMP auth.user > "$VADMIN/user.json")
		$($DUMP flatpages > "$VADMIN/page.json")
		
		$($DUMP vdata.document > "$VDATA/document.json")

		echo 'Finished dump, check the listing is as expected.'
		echo $VDATA
		ls $VDATA -lhtr
		echo $VADMIN
		ls $VADMIN -lhtr
	else
		echo 'Dumping cancelled.'
	fi

elif [ "$1" == "backup" ];
then
	echo 'Making a backup of certain models.'
	# No need to prompt users since the filename changes
	# based upon date and time to second accuracy.
	$($DUMP vdata.format > "$VDATA/format.json.$WHEN")
	$($DUMP vdata.collection > "$VDATA/collection.json.$WHEN")
	$($DUMP vdata.tag > "$VDATA/tag.json.$WHEN")
	$($DUMP vdata.category > "$VDATA/category.json.$WHEN")
	$($DUMP auth.group > "$VADMIN/group.json.$WHEN")
	$($DUMP auth.user > "$VADMIN/user.json.$WHEN")
	$($DUMP flatpages > "$VADMIN/page.json.$WHEN")

	$($DUMP vdata.document > "$VDATA/document.json.$WHEN")
	
	echo 'Finished backup, check the listing is as expected.'
	echo $VDATA
	ls $VDATA -lhtr
	echo $VADMIN
	ls $VADMIN -lhtr
else
	echo 'You can load, dump or backup vocab data.'
fi

