import boto3
import csv
import time
import itertools
import string
import random


response_header_dict = {

     "js":"6daac0b0-9631-4397-ac9d-168a61f52198",
    #  "access-control-max-age":"c4bd80e6-69b9-4db2-9702-c29366b7171a",
     "static":"8500e38d-cf04-4a5c-bf92-5355820093ad",
     "css":"301e8488-ba3e-4049-8987-ee17412319fc",
     "cjs":"e6aa13e8-725e-43e7-acfe-d6742405a1e7"
}


OriginRequestPolicyId = '216adef6-5c7f-47e4-b989-5492eafa07d3'


caching_optimized_policyid_1d = "07fbac48-9973-41f2-8e7f-d9660fe421f8"

caching_optimized_policyid_365 = 'fe1128f8-332e-4189-b3fb-dbcafa87d1bc'

caching_optimized_policyid_7d = 'ed0dc609-67a4-43c0-954f-ba0e1791a4b5'

caching_optimized_policy_nocache = 'd41650ff-6855-45b8-91ba-8ebe2aa44c5c'

cloudfront_fn_dict = {
    "POST": "arn:aws:cloudfront::403858390570:function/deny-post-without-content-length-header",
    "REDIRECT": "arn:aws:cloudfront::439876011496:function/Cloudfront-Girnar-Redirect",
    "REWRITE":"arn:aws:cloudfront::403858390570:function/CloudFront-Redirect",
    "HOSTNAME_REDIRECT":"arn:aws:cloudfront::403858390570:function/CloudFront-Redirect",
    "NA":"NA"
}

behaviors_dict = {}


with open("bikesalesbikedekho.csv", "r") as behavior:
    csvReader = csv.reader(behavior)
    count = 0
    for row in csvReader:
        if row[0] not in behaviors_dict:
            behaviors_dict[row[0]] = {"Origins": [row[2]]}
            behaviors_dict[row[0]]['Alias']=row[0]
            behaviors_dict[row[0]]['ACMCertificateArn']=row[16]
            behaviors_dict[row[0]]["Behaviors"] = [[row[2],row[5],row[3],row[6],row[7],row[9],row[12]]]
        else:
            behaviors_dict[row[0]]['Origins'].append(row[2])
            behaviors_dict[row[0]]["Behaviors"].append([row[2],row[5],row[3],row[6],row[7],row[9],row[12]])

client = boto3.client('cloudfront')

for item in behaviors_dict:
    curr_time = round(time.time()*1000)
    distributionConfig = {
        'Origins':{
            'Quantity':1,
             'Items': []
        },
        'Comment': item,
        'CallerReference': str(curr_time),
        'Aliases': {
            'Quantity': 1,
            'Items': [
                behaviors_dict[item]['Alias']
            ]
        },
        'PriceClass': 'PriceClass_All',
        'Enabled': True,
        'ViewerCertificate': {
            'CloudFrontDefaultCertificate': False,
            'ACMCertificateArn': behaviors_dict[item]['ACMCertificateArn'],
            'SSLSupportMethod': 'sni-only',
            'MinimumProtocolVersion': 'TLSv1.2_2021'
        },
        'HttpVersion' : 'http2and3'
    }
    
    origin_and_path = []
    for i in behaviors_dict[item]['Behaviors']:
        origin_and_path.append([i[0],i[2]])
    origin_and_path.sort()
    set_origin_and_path = list(origin_and_path for origin_and_path,_ in itertools.groupby(origin_and_path))
   
    distributionConfig['Origins']['Quantity'] = len(set_origin_and_path)

    for i in set_origin_and_path:
        N = 5
        res = ''.join(random.choices(string.ascii_uppercase +
                                    string.digits, k=N))
        origin_id = f'{i[0]}-{res}'
        i.append(origin_id)
    

    for i in set_origin_and_path:
        for j in behaviors_dict[item]["Behaviors"]:
            if i[0]==j[0] and i[1]==j[2]:
                j.append(i[2])
        
  
    for i in behaviors_dict[item]['Behaviors']:
        if i[2]!='NA':
            origin = {
            'Id':i[-1],
            'DomainName': i[0],
            'OriginPath': i[1],
            'CustomOriginConfig':{
                'HTTPPort':80,
                'HTTPSPort':443,
                'OriginProtocolPolicy':'https-only',
                'OriginSslProtocols':{
                    'Quantity': 3,
                    'Items':['TLSv1', 'TLSv1.1','TLSv1.2']
                }
            }
            }
        else:
            origin = {
            'Id':i[-1],
            'DomainName': i[0],
            'CustomOriginConfig':{
                'HTTPPort':80,
                'HTTPSPort':443,
                'OriginProtocolPolicy':'https-only',
                'OriginSslProtocols':{
                    'Quantity': 3,
                    'Items':['TLSv1', 'TLSv1.1','TLSv1.2']
                }
            }
            }
        distributionConfig['Origins']['Items'].append(origin)
    
    allowed_methods_count = 0
    allowed_methods = ''

    if behaviors_dict[item]['Behaviors'][0][7] == 'ALL':
        allowed_methods_count = 7
        allowed_methods = ['GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH', 'POST', 'DELETE']
    else:
        allowed_methods_count = 3
        allowed_methods = ['GET', 'HEAD', 'OPTIONS']

    distributionConfig['DefaultCacheBehavior']={
        'TargetOriginId':behaviors_dict[item]['Behaviors'][0][-1],
        'ViewerProtocolPolicy': 'redirect-to-https',
        'AllowedMethods':{
            'Quantity': allowed_methods_count,
            'Items': allowed_methods
        },
        'Compress': True,
        'FunctionAssociations': {
                'Quantity': 1,
                'Items': [
                    {
                        'FunctionARN': cloudfront_fn_dict[behaviors_dict[item]['Behaviors'][0][-3]],
                        'EventType': 'viewer-request'
                    },
                ]
            },
        'ResponseHeadersPolicyId': response_header_dict[behaviors_dict[item]['Behaviors'][0][-2]],
        'CachePolicyId' : caching_optimized_policy_nocache,
        'OriginRequestPolicyId' : OriginRequestPolicyId
    }
    if (cloudfront_fn_dict[behaviors_dict[item]['Behaviors'][0][-3]])=='NA':
        del distributionConfig['DefaultCacheBehavior']['FunctionAssociations']

    distributionConfig['CacheBehaviors']={'Quantity': (len(behaviors_dict[item]['Behaviors'])-1+3+66-2-1+90),'Items':[]}  #add or delete number here if you are getting error for distribution
    if len(behaviors_dict[item]['Behaviors'])>1:
        allowed_methods = ''
        allowed_methods_count = 0
        for i in range(1,len(behaviors_dict[item]['Behaviors'])):
            # if behaviors_dict[item]['Behaviors'][i][7] == 'ALL':
            #     allowed_methods_count = 7
            #     allowed_methods = ['GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH', 'POST', 'DELETE']
            # else:
            #     allowed_methods_count = 3
            #     allowed_methods = ['GET', 'HEAD', 'OPTIONS']
            allowed_methods = 7
            allowed_methods = ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE']
            cachebehavior = {
        'PathPattern': behaviors_dict[item]['Behaviors'][i][1],
        'TargetOriginId':behaviors_dict[item]['Behaviors'][i][-1],
        'ViewerProtocolPolicy': 'redirect-to-https',
        'AllowedMethods':{
            # 'Quantity': allowed_methods_count,
            # 'Items': allowed_methods
            'Quantity': 7,
            'Items':  ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE']
        },
        'Compress': True,
        'FunctionAssociations': {
                'Quantity': 1,
                'Items': [
                    {
                        'FunctionARN': cloudfront_fn_dict[behaviors_dict[item]['Behaviors'][i][-3]],
                        'EventType': 'viewer-request'
                    },
                ]
            },
        'ResponseHeadersPolicyId': response_header_dict[behaviors_dict[item]['Behaviors'][i][-2]],
        'CachePolicyId' : caching_optimized_policy_nocache, ## added cache policy id
        'OriginRequestPolicyId' : OriginRequestPolicyId,

            # 'ForwardedValues': {
        #         'QueryString': True,
        #         'Cookies': {
        #             'Forward': 'none'
        #         },
        #         'Headers': {
        #             'Quantity': 1,
        #             'Items': [
        #                 'Host',
        #             ]
        #         }
        #     },
        #     'MinTTL': 0,
        #     'DefaultTTL': 0,
        #     'MaxTTL': 0
    }
            if (cloudfront_fn_dict[behaviors_dict[item]['Behaviors'][i][-3]])=='NA':
                del cachebehavior['FunctionAssociations']
            distributionConfig['CacheBehaviors']['Items'].append(cachebehavior)



        
def dynamicobject():
    caching_optimized_policyid_1d = caching_optimized_policyid_1d
    extensions_with_responsePolicy = {
        'css': 'css',
        'js': 'js',
        'mjs': 'css',
        'cjs': 'cjs'
    }
    
    for ext, response_policy in extensions_with_responsePolicy.items():
        cache_behavior = {
            'PathPattern': f'/*.{ext}',
            'TargetOriginId': behaviors_dict[item]['Behaviors'][0][-1],
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 3,
                'Items': ['GET', 'HEAD', 'OPTIONS']
            },
            'Compress': True,
            'ResponseHeadersPolicyId': response_header_dict[response_policy],
            'CachePolicyId': caching_optimized_policyid_1d,
            'OriginRequestPolicyId': OriginRequestPolicyId
        }
        
        distributionConfig['CacheBehaviors']['Items'].append(cache_behavior)






def staticobject():
    staticcaching_optimized_policyid = caching_optimized_policyid_1d
    extensions = [
        'aif', 'aiff', 'au', 'avi', 'bin', 'bmp', 'cab', 'carb', 'cct', 'cdf', 'class', 'doc', 'dcr', 'dtd', 'exe', 'flv', 
        'gcf', 'gff', 'gif', 'grv', 'hdml', 'hqx', 'ico', 'ini', 'jpeg', 'jpg', 'mov', 'mp3', 'nc', 'pct', 'pdf', 'png', 
        'ppc', 'pws', 'swa', 'swf', 'txt', 'vbs', 'w32', 'wav', 'wbmp', 'wml', 'wmlc', 'wmls', 'wmlsc', 'xsd', 'zip', 
        'pict', 'tif', 'tiff', 'mid', 'midi', 'ttf', 'eot', 'woff', 'woff2', 'otf', 'svg', 'svgz', 'webp', 'jxr', 'jar', 
        'jp2'
    ]
    
    for ext in extensions:
        cache_behavior = {
            'PathPattern': f'/*.{ext}',
            'TargetOriginId': behaviors_dict[item]['Behaviors'][0][-1],
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 3,
                'Items': ['GET', 'HEAD', 'OPTIONS']
            },
            'Compress': True,
            'ResponseHeadersPolicyId': response_header_dict['static'],
            'CachePolicyId': staticcaching_optimized_policyid,
            'OriginRequestPolicyId': OriginRequestPolicyId
        }
        
        distributionConfig['CacheBehaviors']['Items'].append(cache_behavior)
    
def custombehavior():
    paths = [
        {'PathPattern': '/assetlinks*.json', 'CachePolicyId': caching_optimized_policyid_365},
        {'PathPattern': '/assetlinks.json', 'CachePolicyId': caching_optimized_policyid_365},
        {'PathPattern': '/manifest.json', 'CachePolicyId': caching_optimized_policyid_1d},
        {'PathPattern': '/sw.html', 'CachePolicyId': caching_optimized_policyid_1d}
    ]
    
    for path in paths:
        cache_behavior = {
            'PathPattern': path['PathPattern'],
            'TargetOriginId': behaviors_dict[item]['Behaviors'][0][-1],
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 3,
                'Items': ['GET', 'HEAD', 'OPTIONS']
            },
            'Compress': True,
            'ResponseHeadersPolicyId': response_header_dict['static'],
            'CachePolicyId': path['CachePolicyId'],
            'OriginRequestPolicyId': OriginRequestPolicyId
        }
        
        distributionConfig['CacheBehaviors']['Items'].append(cache_behavior)


dynamicobject()
staticobject()
custombehavior()


client.create_distribution(DistributionConfig=distributionConfig)
