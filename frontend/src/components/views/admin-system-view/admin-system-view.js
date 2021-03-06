// Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

angular.module('appenlight.components.adminSystemView', [])
    .component('adminSystemView', {
        templateUrl: 'components/views/admin-system-view/admin-system-view.html',
        controller: AdminSystemViewController
    });

AdminSystemViewController.$inject = ['sectionViewResource'];

function AdminSystemViewController(sectionViewResource) {
    var vm = this;
    vm.tables = [];
    vm.loading = {system: true};
    sectionViewResource.get({
        section: 'admin_section',
        view: 'system'
    }, null, function (data) {
        vm.DBtables = data.db_tables;
        vm.ESIndices = data.es_indices;
        vm.queueStats = data.queue_stats;
        vm.systemLoad = data.system_load;
        vm.packages = data.packages;
        vm.processInfo = data.process_info;
        vm.disks = data.disks;
        vm.memory = data.memory;
        vm.selfInfo = data.self_info;

        vm.loading.system = false;
    });
};
