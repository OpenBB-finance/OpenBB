import pandas as pd
import traitlets
import ipyvuetify as v
import json

import ipywidgets
from threading import Timer


class RenderDF(v.VuetifyTemplate):
    """
    Vuetify DataTable rendering of a pandas DataFrame

    Args:
        data (DataFrame) - the data to render
        title (str) - optional title
    """

    headers = traitlets.List([]).tag(sync=True, allow_null=True)
    items = traitlets.List([]).tag(sync=True, allow_null=True)
    title = traitlets.Unicode("DataFrame").tag(sync=True)
    index_col = traitlets.Unicode("").tag(sync=True)
    template = traitlets.Unicode(
        """
        <template>
          <v-card>
            <v-card-title>
              <span class="title font-weight-bold">{{ title }}</span>
              <v-spacer></v-spacer>
            </v-card-title>
            <v-data-table
                :headers="headers"
                :items="items"
                :item-key="index_col"
            >
                <template v-slot:no-data>
                  <v-alert :value="true" color="error" icon="mdi-alert">
                    Sorry, nothing to display here :(
                  </v-alert>
                </template>
            </v-data-table>
          </v-card>
        </template>
        """
    ).tag(sync=True)

    def __init__(self, *args, data=pd.DataFrame(), title=None, **kwargs):
        super().__init__(*args, **kwargs)
        data = data.reset_index()
        self.index_col = data.columns[0]
        headers = [{"text": col, "value": col} for col in data.columns]
        headers[0].update({"align": "left", "sortable": True})
        self.headers = headers
        self.items = json.loads(data.to_json(orient="records"))
        if title is not None:
            self.title = title
