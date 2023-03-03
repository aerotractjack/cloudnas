from pathlib import Path
import boto3

class Walker:
    ''' utility class to recursively walk directory and yield
    all files and folders (within breadth and depth restrictions) '''

    def __init__(self, filemax=None, depthmax=None):
        ''' 
        Params:
            filemax (int): maximum number of files to yield from any directory
            depthmax (int): maximum recursion depth 
        '''
        self.fmax = filemax
        self.dmax = depthmax
        self.ignore = [".DS_Store", "._.DS_Store", "@eaDir"]

    def check_ignore(self, file):
        '''
        Some files, such as system or NAS metadata, need to be ignored.
        Params:
            file (pathlib.Path): file to possibly be ignored
        '''
        name = file.name
        return name in self.ignore

    def walk(self, target_path, count=0, depth=0):
        '''
        Recursively walk directory yielding filenames while respecting 
        breadth and depth restrictions.
        Params:
            target_path(str or pathlib.Path): top-level directory to start walk
            count (int): number of files visited at this level (user: do not set)
            depth (int): current recursion depth (user: do not set)
        Yields:
            file (pathlib.Path): path object of visited file
        '''
        if not isinstance(target_path, Path):
            target_path = Path(target_path)
        if self.dmax is not None and depth > self.dmax:
            return
        for file in target_path.iterdir():
            if self.check_ignore(file):
                continue
            if file.is_dir():
                for r in self.walk(file, depth=depth+1):
                    yield r
            else:
                count += 1
                if self.fmax is None or count <= self.fmax:
                    yield file

class Uploader:
    ''' utility class to handle uploading data to S3 '''

    def __init__(self, prefix, bucket):
        '''
        Params:
            prefix (str or pathlib.Path): common prefix for all files being uploaded (ex: /home/user/NAS/main)
            bucket (str): name of S3 bucket to upload into
        '''
        self.prefix = Path(prefix) if not isinstance(prefix, Path) else prefix
        self.bucket = bucket

    def create_cloud_filename(self, local_filename):
        '''
        Create the cloud filename by removing the common prefix from the local filename.
        Params:
            local_filename (str or pathlib.Path): Path to local file we are uploading
        Returns:
            cloud_filename (pathlib.Path): Path to data in S3 (local path without common prefix)
        '''
        if not isinstance(local_filename, Path):
            local_filename = Path(local_filename)
        return local_filename.relative_to(self.prefix)
       
    def upload(self, local_filename):
        '''
        Upload a file from the local computer into the S3 bucket.
        Params:
            local_filename (pathlib.Path): Path to local file being uploaded
        Returns:
            cloud_filename (str): String repr of path to uploaded file within S3
        '''
        s3 = boto3.client("s3")
        cloud_filename = self.create_cloud_filename(local_filename)
        local_filename = local_filename.as_posix()
        cloud_filename = cloud_filename.as_posix()
        s3.upload_file(local_filename, self.bucket, cloud_filename)
        return cloud_filename

def NAStoS3(pref, stors, filemax=None, depthmax=None):
    '''
    Wraps functionality of the Walker() and Uploader() classes to
    explore and upload local files to S3.
    Params:
        pref (str or pathlib.Path): common path prefix of all files (ex /home/user/NAS/main)
        stors (list[str or pathlib.Path]): list of top-level directories to walk and upload
        filemax (int or None): maximum amount of files to visit per directory
        depthmax (int or None): maximum recursion depth/depth of directories to visit
    Yields:
        cloud_filename (str): String repr of path to uploaded file within S3
    '''
    walker = Walker(filemax=filemax, depthmax=depthmax)
    uploader = Uploader(pref, "clients-aerotract")

    for stor in stors:
        print(stor)
        for f in walker.walk(stor):
            yield uploader.upload(f)

if __name__ == '__main__':
    pref = "/home/coryg/NAS/main"
    stors = [
        "/home/coryg/NAS/main/Clients/Weyerhauser",
        "/home/coryg/NAS/main/Clients/Manulife",
    ]
    for f in NAStoS3(pref, stors, filemax=5):
        print(f)