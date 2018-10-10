import falcon

from bayesapi.resources import BaseResource
from bayesapi.validation import validate
import bayesapi.history

def add_anomaly_data(cfg, result):
    last_q_data = bayesapi.history.read(cfg, "anomaly")

    q_data = {}
    for r in last_q_data['result']:
        q_data[r['row-id']] = r['probability']

    for r in result:
        r['probability'] = q_data[r['row-id']]

    return result


def add_similarity_data(cfg, result):
    last_q_data = bayesapi.history.read(cfg, "similarity")

    q_data = {}
    for r in last_q_data['result']:
        q_data[r['row-id']] = r['similarity']

    for r in result:
        r['similarity'] = q_data[r['row-id']]

    return result


class ColumnDataResource(BaseResource):

    def on_post(self, req, resp):

        req_vars = validate(self.api_def, 'post', req)

        table_name = self.cfg.table_name

        def fix_fips(k, v):
            if k == self.fips['state']:
                sv = str(v)
                return sv.zfill(2)
            elif k == self.fips['county']:
                sv = str(v)
                return sv.zfill(5)
            return v

        def fix_fips_if_present(result):
            return { k : fix_fips(k, v) for k, v in result.iteritems() }

        def normalize(column):
            return column.lower()

        columns = [normalize(c) for c in req_vars['columns']]

        include_anomaly_value = False
        include_similarity_value = False

        try:
            columns.remove(u'probability')
            include_anomaly_value = True
        except ValueError:
            pass

        try:
            columns.remove(u'similarity')
            include_similarity_value = True
        except ValueError:
            pass

        with self.bdb.savepoint():
            def column_name_set():
                query = self.queries.get_full_table(table_name=table_name)
                cursor = self.execute(query)
                return {normalize(tuple[0]) for tuple in cursor.description}

            for c in columns:
                if normalize(c) not in column_name_set():
                    resp.status = 400
                    return

        result = []

        with self.bdb.savepoint():
            if len(columns) > 0:
                query = self.queries.column_data(
                    column_names = ['"{}"'.format(c) for c in columns],
                    table_name = '"{}"'.format(table_name)
                )
            else:
                query = self.queries.row_id_data(
                    table_name = '"{}"'.format(table_name)
                )

            cursor = self.execute(query)

            db_col_names = [k for k in columns]
            db_col_names.insert(0, 'row-id')

            result = [ dict(zip(db_col_names, row)) for row in cursor ]


        if include_anomaly_value:
            add_anomaly_data(self.cfg.history, result)

        if include_similarity_value:
            add_similarity_data(self.cfg.history, result)

        resp.media = [fix_fips_if_present(r) for r in result]
        resp.status = falcon.HTTP_200
