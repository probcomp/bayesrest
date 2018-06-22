import jsonschema
import falcon


def validate(api_def, method, req):
    api_params = api_def[method]['parameters']

    errors = []
    result = {}

    for p in api_params:
        v = req.media.get(p['name'])

        ## required?
        if p['required'] is True and v is None:
            errors.append("The parameter `{}` ({}) is required, but was missing from your request.".format(p['name'], p['description']))

        result[p['name']] = v

        if v is None:
            continue

        ## type ok?
        schema = p['schema']
        try:
            jsonschema.validate(v, schema)
        except jsonschema.ValidationError as e:
            errors.append(str(e))

    if errors:
        raise falcon.HTTPBadRequest(
            'Problems with your request.',
            " | ".join(errors)
        )

    return result
