import boto3

def update_response_headers_policy_for_paths_and_extensions(distribution_id, new_response_headers_policy_id, extensions, specific_paths, path_patterns):
    client = boto3.client('cloudfront')


    response = client.get_distribution_config(Id=distribution_id)
    distribution_config = response['DistributionConfig']
    etag = response['ETag']


    def is_matching_behavior(path_pattern):

        if path_pattern in specific_paths:
            return True

        for pattern in path_patterns:
            if path_pattern.startswith(pattern.replace('*', '')):
                return True

        extension = path_pattern.split('.')[-1]

        return extension in extensions


    if 'DefaultCacheBehavior' in distribution_config:
        distribution_config['DefaultCacheBehavior']['ResponseHeadersPolicyId'] = new_response_headers_policy_id

    if 'CacheBehaviors' in distribution_config and 'Items' in distribution_config['CacheBehaviors']:
        for behavior in distribution_config['CacheBehaviors']['Items']:
            if is_matching_behavior(behavior['PathPattern']):
                behavior['ResponseHeadersPolicyId'] = new_response_headers_policy_id

 
    response = client.update_distribution(
        Id=distribution_id,
        IfMatch=etag,
        DistributionConfig=distribution_config
    )

    return response


distribution_id = 'E25ISQGCQPP9GS'
new_response_headers_policy_id = '706b2413-b5f5-4b5d-80fe-54f6a275ea77'

extensions = [
    'aif', 'aiff', 'au', 'avi', 'bin', 'bmp', 'cab', 'carb', 'cct', 'cdf', 'class', 'doc', 'dcr', 'dtd', 'exe', 'flv', 
    'gcf', 'gff', 'gif', 'grv', 'hdml', 'hqx', 'ico', 'ini', 'jpeg', 'jpg', 'mov', 'mp3', 'nc', 'pct', 'pdf', 'png', 
    'ppc', 'pws', 'swa', 'swf', 'txt', 'vbs', 'w32', 'wav', 'wbmp', 'wml', 'wmlc', 'wmls', 'wmlsc', 'xsd', 'zip', 
    'pict', 'tif', 'tiff', 'mid', 'midi', 'ttf', 'eot', 'woff', 'woff2', 'otf', 'svg', 'svgz', 'webp', 'jxr', 'jar', 
    'jp2'
]

specific_paths = [
    '/sw.html', '/sw-helper-iframe.html', '/robots.txt', '/workers/worker.js', '/serviceworker.js', 
    '/manifest.json', '/workers/native-widget-script-amp.min.js'
]

path_patterns = [
    '/user-reviews/*/*/*'
]

response = update_response_headers_policy_for_paths_and_extensions(distribution_id, new_response_headers_policy_id, extensions, specific_paths, path_patterns)
