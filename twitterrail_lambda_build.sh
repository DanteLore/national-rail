#!/bin/bash

ROOT=`pwd`
TARGET=/tmp/twitterrail-lambda-target
ZIP=~/twitterrail_lambda.zip
SOURCE_FILES=(twitterrail twitterrail_lambda.py)
LIBRARIES=(requests datetime logging xmltodict twitter os base64)

# Create the temp target dir
mkdir ${TARGET}
cd ${TARGET}

# Copy the source files over
for F in ${SOURCE_FILES[@]}; do
    cp -Rf ${ROOT}/${F} ${TARGET}
done

# Install the libraries
for L in ${LIBRARIES[@]}; do
    pip install ${L} -t ${TARGET}
done

# Create the zip file
zip -r ${ZIP} *

# Clean up
rm -rf ${TARGET}
