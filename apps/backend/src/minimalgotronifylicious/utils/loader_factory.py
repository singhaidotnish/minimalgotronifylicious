from src.minimalgotronifylicious.config_loader.data_loader.yaml_loader import YamlLoader
# from loaders.json_loader import JsonLoader  # future
# from loaders.db_loader import DatabaseLoader  # future

def get_loader(source_type: str, path_or_conn: str):
    """
    Returns an instance of a data loader based on the source type.

    :param source_type: Type of data source ('yaml', 'json', 'db', etc.)
    :param path_or_conn: File path or connection string
    :return: Instance of a loader implementing DataLoader
    """
    if source_type == "yaml":
        return YamlLoader(path_or_conn)

    # elif source_type == "json":
    #     return JsonLoader(path_or_conn)

    # elif source_type == "db":
    #     return DatabaseLoader(path_or_conn)

    else:
        raise ValueError(f"Unsupported data source type: {source_type}")
