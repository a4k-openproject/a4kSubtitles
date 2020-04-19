#!/bin/bash

token=$1
user="newt-sc"
repo="a4kSubtitles"
sha="$(git rev-parse HEAD)"
ver=$(git show -s --format=%s)
tag_ver="${ver#?}"
tag="service.subtitles.a4ksubtitles/service.subtitles.a4ksubtitles-$tag_ver"
api="https://api.github.com/repos/$user/$repo"

if [ ${#ver} -ge 7 ]; then
    echo 'skipping release'
    exit
fi

generate_release_data()
{
  cat <<EOF
{
  "tag_name": "$tag",
  "name": "$ver"
}
EOF
}

post_data="$(generate_release_data)"

echo "Create release"
echo "$post_data"

curl \
    --header "Authorization: token $token" \
    --header "Accept: application/vnd.github.v3+json" \
    --data "$post_data" \
    "$api/releases"
