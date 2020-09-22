set -e

data_dir=/srv/data1/speech/public/online_meeting/itb/arsip_pelabelan/
prev_version=$data_dir/v1.1.0/csv/
curr_version=$data_dir/v2.1.0/csv/

## get all files in previous directory
## for all files, check if is exist in new directory? if not exist make link. Its link? if yes, get the source file


function list_include_item {
  local list="$1"
  local item="$2"
  if [[ $list =~ (^|[[:space:]])"$item"($|[[:space:]]) ]] ; then
    result=0
  else
    result=1
  fi
  return $result
}

files_prev_ver=$(ls $prev_version)
files_curr_ver=$(ls $curr_version)
len_prev_ver=$(wc -w <<< $files_prev_ver)
len_curr_ver=$(wc -w <<< $files_curr_ver)
echo
echo "INFO Total files in previous version $len_prev_ver"
echo "INFO Total files in current version $len_curr_ver"
echo

for file in $files_prev_ver; do
	if `list_include_item "$files_curr_ver" "$file"` ; then
		# if [[ -L $curr_version/$file ]]; then
		# 	rm $curr_version/$file
		# 	echo "Remove $file"
		# else
			echo "$file exist both in previous and current version"
		# fi
	else 
		if [[ -L "$prev_version/$file" ]]; then ## unapprove
			real_source=$(readlink -f $file)
			ln -s $real_source $curr_version
			echo "Linked into real source $real_source"
		else
			ln -s $prev_version/$file $curr_version
			echo "Linked into $prev_version/$file"
		fi
	fi
done
