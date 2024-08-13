
import boto3

def update_response_headers_policy_for_css_js_mjs(distribution_id, css_policy_id, js_policy_id, mjs_policy_id, cjs_policy_id):
    client = boto3.client('cloudfront')

    # Get the current distribution configuration
    response = client.get_distribution_config(Id=distribution_id)
    distribution_config = response['DistributionConfig']
    etag = response['ETag']

    # Function to determine which policy to apply based on file extension
    def get_policy_id_for_extension(path_pattern):
        if path_pattern.endswith('.css'):
            return css_policy_id
        elif path_pattern.endswith('.js'):
            return js_policy_id
        elif path_pattern.endswith('.mjs'):
            return mjs_policy_id
        elif path_pattern.endswith('.cjs'):
            return cjs_policy_id
        return None

    # Update the cache behaviors based on the file extension
    if 'CacheBehaviors' in distribution_config and 'Items' in distribution_config['CacheBehaviors']:
        for behavior in distribution_config['CacheBehaviors']['Items']:
            policy_id = get_policy_id_for_extension(behavior['PathPattern'])
            if policy_id:
                behavior['ResponseHeadersPolicyId'] = policy_id

    # Update the distribution configuration
    response = client.update_distribution(
        Id=distribution_id,
        IfMatch=etag,
        DistributionConfig=distribution_config
    )

    return response

# Example usage:
distribution_id = 'EPEO63DABYN5B'
css_policy_id = '301e8488-ba3e-4049-8987-ee17412319fc'
js_policy_id = '6daac0b0-9631-4397-ac9d-168a61f52198'
mjs_policy_id = 'cb37e117-42e8-45c9-9662-c16f8d87a30b'
cjs_policy_id = 'e6aa13e8-725e-43e7-acfe-d6742405a1e7'
response = update_response_headers_policy_for_css_js_mjs(distribution_id, css_policy_id, js_policy_id, mjs_policy_id, cjs_policy_id)

