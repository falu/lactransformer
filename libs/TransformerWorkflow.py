try:
    import traceback
    import logging
    import multiprocessing
    from libs import LasPyConverter, TxtPanPyConverter, FriendlyName, AssignProjection
except ImportError as err:
    print('Error import module: {0}'.format(err))
    exit(128)


def Transformer(parameters):
    # Parse incoming parameters
    source_file = parameters[0]
    destination_file = parameters[1]
    source_projection = parameters[2]
    destination_projection = parameters[3]
    input_format = parameters[4]
    full_header_update = parameters[5]
    txt_separator = parameters[6]
    # Get name for this process
    current = multiprocessing.current_process()
    proc_name = current.name
    # Define friendly name of input formats
    input_format_name = FriendlyName.FriendlyName(input_format)
    logging.info('[%s] Starting ...' % (proc_name))
    if input_format in ['las', 'laz']:
        logging.info(
            '[%s] Opening %s %s file for converting to %s %s file ...' % (
                proc_name, source_file, input_format_name, destination_file, input_format_name))
        logging.info(
            '[%s] Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, AssignProjection.AssignProjectionName(source_projection), AssignProjection.AssignProjectionName(destination_projection)))
        # Opening source LAS files for read and write
        try:
            lasFiles = LasPyConverter.LasPyConverter(
                source_file, source_projection, destination_file, destination_projection)
            lasFiles.Open()
        except ValueError as err:
            logging.error(
                'Cannot open files: %s and %s, error: %s. Probably this type of errors (ValueError) caused by corrupt LAS PointCloud file.' % (
                    source_file, destination_file, str(err)))
            traceback.print_exc()
            exit(10)
        except Exception as err:
            logging.error('Cannot open files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            traceback.print_exc()
            exit(10)
        try:
            logging.info('[%s] Scaling %s.' % (proc_name, input_format_name))
            lasFiles.GetSourceScale()
            original, transformed = lasFiles.SetDestinationScale()
            logging.info('[%s] %s file original/transformed offset: [%.2f,%.2f,%.2f]/[%.2f,%.2f,%.2f] coordinates.' % (
                proc_name, input_format_name, original[0], original[1], original[2], transformed[0], transformed[1],
                transformed[2]))
            original_min = lasFiles.ReturnOriginalMin()
            original_max = lasFiles.ReturnOriginalMax()
            logging.info('[%s] Bounding box of original PointCloud min: [%.2f,%.2f,%.2f] max: [%.2f,%.2f,%.2f].' % (
                proc_name, original_min[0], original_min[1], original_min[2], original_max[0], original_max[1],
                original_max[2]))
            logging.info('[%s] Transforming %s.' % (proc_name, input_format_name))
            lasFiles.TransformPointCloud()
        except Exception as err:
            logging.error(
                'Cannot transform files form %s to %s, error: %s.' % (source_file, destination_file, str(err)))
            traceback.print_exc()
            exit(11)
        else:
            logging.info('[%s] Successfully transformed %s data for file: %s.' % (
                proc_name, input_format_name, destination_file))
            transformed_min = lasFiles.ReturnTransformedMin()
            transformed_max = lasFiles.ReturnTransformedMax()
            logging.info('[%s] Bounding box of transformed PointCloud min: [%.2f,%.2f,%.2f] max: [%.2f,%.2f,%.2f].' % (
                proc_name, transformed_min[0], transformed_min[1], transformed_min[2], transformed_max[0], transformed_max[1],
                transformed_max[2]))
        try:
            logging.info('[%s] Closing transformed %s %s file.' % (proc_name, destination_file, input_format_name))
            lasFiles.Close(full_header_update)
        except Exception as err:
            logging.error('Cannot close files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[%s] Transformed %s %s file has created.' % (proc_name, destination_file, input_format_name))
            return 0
    elif input_format in ['txt', 'lastxt', 'iml', 'csv', 'pef', 'strtxt', 'listtxt']:
        logging.info(
            '[%s] Opening %s %s file for converting to %s %s file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, input_format_name, destination_file, input_format_name, source_projection,
                destination_projection))
        # Opening source Text pointcloud files for read and write
        try:
            txtFiles = TxtPanPyConverter.TxtPanPyConverter(source_file, source_projection, destination_file,
                                                           destination_projection, input_format, txt_separator)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        try:
            txtFiles.Transform()
        except Exception as err:
            logging.error(
                'Cannot transform files form %s to %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(11)
        else:
            logging.info(
                '[%s] Successfully transformed %s for file: %s.' % (proc_name, input_format_name, destination_file))
        try:
            logging.info('[%s] Closing transformed %s %s file.' % (proc_name, destination_file, input_format_name))
            txtFiles.Close()
        except Exception as err:
            logging.error('Cannot close files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[%s] Transformed %s %s file has created.' % (proc_name, destination_file, input_format_name))
            return 0
    else:
        logging.critical('Unknown -input_format parameter is specified: "{0}".'.format(input_format))
