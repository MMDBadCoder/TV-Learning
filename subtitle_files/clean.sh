subtitle_number=6
old_subtitle_name="${subtitle_number}.srt"
new_subtitle_name="new-${subtitle_number}.srt"
iconv -f utf-8 -t utf-8 -c "${old_subtitle_name}" >"${new_subtitle_name}"
mv "${new_subtitle_name}" "${old_subtitle_name}"
