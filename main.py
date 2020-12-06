from create_annotations import *
import argparse
from category_colors import *
parser = argparse.ArgumentParser()

# Get 'images' and 'annotations' info 
def images_annotations_info(maskpath):
    # This id will be automatically increased as we go
    annotation_id = 1

    annotations = []
    images = []
    
    # Get absolute paths of all files in a directory
    mask_images = absolute_file_paths(maskpath)
    
    #get number of masks
    number_of_masks = len(mask_images)
    print("found " + str(number_of_masks) + " masks")
    
    start = 1
    
    for image_id, mask_image in enumerate(mask_images, 1):
        file_name = os.path.basename(mask_image).split('.')[0] + ".jpg"
        print("treating mask "+str(start)+" / "+str(number_of_masks) +" ("+str(round(start/number_of_masks*100,1))+"%"+") " + file_name)
        start = start + 1
        
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dataset", help="dataset location",default='dataset/')
    parser.add_argument("-o", "--output", help="output directory",default='output/')
    parser.parse_args()
    datasetpath = parser.parse_args().dataset
    outputpath = parser.parse_args().output
    print("dataset path : " + datasetpath)
    print("output path : " + outputpath)

    for keyword in ['train', 'val']:
        mask_path = datasetpath + '{}_mask'.format(keyword)
        coco_format['images'], coco_format['annotations'] = images_annotations_info(mask_path)
        print("exporting json")
        with open(outputpath + '{}.json'.format(keyword),'w') as outfile:
            json.dump(coco_format, outfile)