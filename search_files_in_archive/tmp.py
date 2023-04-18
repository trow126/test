def search_files_in_archive(path_or_data, target_ext, parent_path='', file_name=None):
    file_paths = []

    if isinstance(path_or_data, io.BytesIO):
        file_data = path_or_data
        archive_obj = open_archive(file_data, file_name)
    else:
        if os.path.isfile(path_or_data):
            with open(path_or_data, 'rb') as file_data:
                archive_obj = open_archive(file_data, path_or_data)
        elif os.path.isdir(path_or_data):
            for root, _, files in os.walk(path_or_data):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_paths.extend(search_files_in_archive(file_path, target_ext))
            return file_paths
        else:
            return []

    if archive_obj:
        if isinstance(archive_obj, zipfile.ZipFile):
            for member in archive_obj.infolist():
                full_path = parent_path + '/' + member.filename
                if member.filename.endswith(target_ext):
                    file_paths.append(full_path)
                elif not member.is_dir():
                    with archive_obj.open(member) as file_data:
                        inner_archive = open_archive(file_data, member.filename)
                        if inner_archive:
                            file_paths.extend(search_files_in_archive(inner_archive, target_ext, full_path))
        elif isinstance(archive_obj, tarfile.TarFile):
            for member in archive_obj.getmembers():
                full_path = parent_path + '/' + member.name
                if member.name.endswith(target_ext):
                    file_paths.append(full_path)
                    file_data = archive_obj.extractfile(member)
                elif not member.isdir():
                    file_data = archive_obj.extractfile(member)
                    if file_data:
                        inner_archive = open_archive(file_data, member.name)
                        if inner_archive:
                            file_paths.extend(search_files_in_archive(inner_archive, target_ext, full_path))
        elif isinstance(archive_obj, (gzip.GzipFile, bz2.BZ2File)):
            file_data = io.BytesIO(archive_obj.read())
            inner_archive = open_archive(file_data)
            if inner_archive:
                file_paths.extend(search_files_in_archive(inner_archive, target_ext, parent_path))

    return file_paths
