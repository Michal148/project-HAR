#!/bin/bash

REPO_NAME=$1

# function to get the tag of a Docker image
get_image_tag() {
    local image_name="$1"
    local current_tag=$(docker images --format '{{.Tag}}' "$image_name" 2>/dev/null)
    
    if [ -n "$current_tag" ]; then
        local new_tag=$(echo "$current_tag")
        echo "$new_tag"
    else
        echo "Image '$image_name' not found or has no tag."
    fi
}

# get the current tags for feature_extractor and ml_predictor images
CURR_FEATURE_EXTRACTOR_TAG=$(get_image_tag "feature_extractor")
CURR_ML_PREDICTOR_TAG=$(get_image_tag "ml_predictor")

# increment the tags by 0.1 to create new tags
NEW_FEATURE_EXTRACTOR_TAG=$(echo "$CURR_FEATURE_EXTRACTOR_TAG + 0.1" | bc)
NEW_ML_PREDICTOR_TAG=$(echo "$CURR_ML_PREDICTOR_TAG + 0.1" | bc)

# check if the feature_extractor image exists
FEATURE_EXTRACTOR=$(docker images -q feature_extractor:$CURR_FEATURE_EXTRACTOR_TAG)
if [ -z "$FEATURE_EXTRACTOR" ]; then
    echo "Feature extractor image doesn't exist."
else
    echo "Feature extractor image exists."
    docker rmi feature_extractor:$CURR_FEATURE_EXTRACTOR_TAG --force 
    echo "Old feature extractor image deleted."
    echo "Building new image..."
    cd ../feature-extractor
    docker build -t feature_extractor:$NEW_FEATURE_EXTRACTOR_TAG .
    echo "New feature extractor image built with tag: $NEW_FEATURE_EXTRACTOR_TAG."
fi

# check if the ml_predictor image exists
ML_PREDICTOR=$(docker images -q ml_predictor:$CURR_ML_PREDICTOR_TAG)
if [ -z "$ML_PREDICTOR" ]; then
    echo "ML predictor image doesn't exist."
else
    echo "ML predictor image exists."
    docker rmi ml_predictor:$CURR_ML_PREDICTOR_TAG --force
    echo "Old ML predictor image deleted."
    echo "Building new image..."
    cd ../ML-model
    docker build -t ml_predictor:$NEW_ML_PREDICTOR_TAG .
    echo "New ML predictor image built with tag: $NEW_ML_PREDICTOR_TAG."
fi

# push images to given registry
docker tag feature_extractor:$NEW_FEATURE_EXTRACTOR_TAG $REPO_NAME/feature_extractor:$NEW_FEATURE_EXTRACTOR_TAG
docker push $REPO_NAME/feature_extractor:$NEW_FEATURE_EXTRACTOR_TAG

docker tag ml_predictor:$NEW_ML_PREDICTOR_TAG $REPO_NAME/ml_predictor:$NEW_ML_PREDICTOR_TAG
docker push $REPO_NAME/ml_predictor:$NEW_ML_PREDICTOR_TAG