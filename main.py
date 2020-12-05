from create_annotations import *

# Define which colors match which categories in the images
category_ids = {
    '(64, 32, 32)': 0, # road 
    '(255, 0, 0)': 1, # lane markings
    '(128, 128, 96)': 2, # undrivable
    '(0, 255, 102)': 3, # movable 
    '(204, 0, 255)': 4, # my car
}

# Get 'images' and 'annotations' info 
def images_annotations_info(maskpath):
    # This id will be automatically increased as we go
    annotation_id = 1

    annotations = []
    images = []
    
    # Get absolute paths of all files in a directory
    mask_images = absolute_file_paths(maskpath)
    
    for image_id, mask_image in enumerate(mask_images, 1):
        file_name = os.path.basename(mask_image).split('.')[0] + ".jpg"

        # image shape
        mask_image_open = Image.open(mask_image)
        w, h = mask_image_open.size
        
        # 'images' info 
        image = create_image_annotation(file_name, w, h, image_id)
        images.append(image)

        sub_masks = create_sub_masks(mask_image_open, w, h)
        for color, sub_mask in sub_masks.items():
            category_id = category_ids[color]

            # 'annotations' info
            polygons, segmentations = create_sub_mask_annotation(sub_mask)

            # Three labels are multipolygons in our case: wall, roof and sky
            if(category_id == 2 or category_id == 5 or category_id == 6):
                # Combine the polygons to calculate the bounding box and area
                multi_poly = MultiPolygon(polygons)
                                
                annotation = create_annotation_format(multi_poly, segmentations, image_id, category_id, annotation_id)

                annotations.append(annotation)
                annotation_id += 1
            else:
                for i in range(len(polygons)):
                    # Cleaner to recalculate this variable
                    segmentation = [np.array(polygons[i].exterior.coords).ravel().tolist()]
                    
                    annotation = create_annotation_format(polygons[i], segmentation, image_id, category_id, annotation_id)
                    
                    annotations.append(annotation)
                    annotation_id += 1
        
    return images, annotations

if __name__ == '__main__':
    for keyword in ['train', 'val']:
        mask_path = 'dataset/{}_mask'.format(keyword)
        coco_format['images'], coco_format['annotations'] = images_annotations_info(mask_path)
        #print(json.dumps(coco_format))
        with open('output/{}.json'.format(keyword),'w') as outfile:
            json.dump(coco_format, outfile)