try:
    import csv
    import re
    from pyproj import Proj, transform
    from lib import PefFile
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)


class TxtPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename, destination_projection, type='txt',
                 separator=','):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProj = Proj(source_projection)
        self.__DestinationProjection = destination_projection
        self.__DestinationProj = Proj(destination_projection)
        self.__Separator = separator
        self.__Type = type

    def Open(self):
        try:
            if self.__Type != 'pef':
                self.__SourceOpenedFile = open(self.__SourceFileName, 'rb')
                self.__DestinationOpenedFile = open(self.__DestinationFileName, 'wb')
            elif self.__Type == 'pef':
                self.__SourceOpenedFile = PefFile.PefFile(self.__SourceFileName)
                self.__SourceOpenedFile.OpenRO()
                self.__DestinationOpenedFile = PefFile.PefFile(self.__DestinationFileName)
                self.__DestinationOpenedFile.OpenOW()
        except Exception as err:
            raise

    def OpenReanOnly(self):
        try:
            self.__SourceOpenedFile = open(self.__SourceFileName, 'rb')
            self.__DestinationOpenedFile = open(self.__DestinationFileName, 'wb')
        except Exception as err:
            raise

    def TransformLASText(self):
        # Transforming PointText
        r = csv.reader(self.__SourceOpenedFile, delimiter=self.__Separator)
        w = csv.writer(self.__DestinationOpenedFile, delimiter=self.__Separator)
        for i, row in enumerate(r):
            row[0], row[1], row[2] = transform(self.__SourceProj, self.__DestinationProj,
                                               row[0], row[1], row[2])
            w.writerow(row)

    def TransformPointText(self):
        # Transforming PointText
        r = csv.reader(self.__SourceOpenedFile, delimiter=self.__Separator)
        w = csv.writer(self.__DestinationOpenedFile, delimiter=self.__Separator)
        for i, row in enumerate(r):
            if i > 0:  # skip header transformation
                row[1], row[2], row[3] = transform(self.__SourceProj, self.__DestinationProj,
                                                   row[1], row[2], row[3])
            w.writerow(row)

    def TransformPointCSV(self):
        # Transforming PointText
        r = csv.reader(self.__SourceOpenedFile, self.__Separator)
        w = csv.writer(self.__DestinationOpenedFile, self.__Separator)
        for i, row in enumerate(r):
            if i > 0:  # skip header transformation
                row[2], row[3], row[4] = transform(self.__SourceProj, self.__DestinationProj,
                                                   row[2], row[3], row[4])
            w.writerow(row)

    def TransformPointIML(self):
        # Transforming PointText
        r = csv.reader(self.__SourceOpenedFile, delimiter=' ')
        w = csv.writer(self.__DestinationOpenedFile, delimiter=' ')
        for i, row in enumerate(r):
            if i > 0:  # skip header transformation
                row[1], row[2], row[3] = transform(self.__SourceProj, self.__DestinationProj,
                                                   row[1], row[2], row[3])
            w.writerow(row)

    def TransformPEF(self):
        point_pattern = re.compile('P\d{1,3}')  # format is Pn or Pnn or Pnnn
        while True:
            Content = self.__SourceOpenedFile.ReadNextItem()
            if not Content:
                break
            # self.__DestinationOpenedFile.
            for i, row in enumerate(Content):
                point_number = point_pattern.search(row[0])
                if point_number is not None:
                    coordinates = row[1].split(' ')
                    coordinates[0], coordinates[1], coordinates[2] = transform(self.__SourceProj,
                                                                               self.__DestinationProj,
                                                                               coordinates[0], coordinates[1],
                                                                               coordinates[2])
                    Content[i][1] = '%s %s %s' % (coordinates[0], coordinates[1], coordinates[2])
            self.__DestinationOpenedFile.WriteNextItem(Content)

    def Close(self, type='txt'):
        if self.__Type != 'pef':
            self.__SourceOpenedFile.close()
            self.__DestinationOpenedFile.close()
        elif self.__Type == 'pef':
            self.__SourceOpenedFile.Close()
            self.__DestinationOpenedFile.Close()
