// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef CHROME_BROWSER_SW_PROCESSES_FORENSICS_H__
#define CHROME_BROWSER_SW_PROCESSES_FORENSICS_H__

#include <vector>

#include "base/macros.h"
#include "chrome/browser/task_manager/task_manager_observer.h"
#include "extensions/browser/browser_context_keyed_api_factory.h"
#include "extensions/browser/event_router.h"
#include "extensions/browser/extension_event_histogram_value.h"
#include "extensions/browser/extension_function.h"


class ProcessesApiTest;

namespace sw_forensics {

enum ProcessType {
  PROCESS_TYPE_NONE,
  PROCESS_TYPE_BROWSER,
  PROCESS_TYPE_RENDERER,
  PROCESS_TYPE_EXTENSION,
  PROCESS_TYPE_NOTIFICATION,
  PROCESS_TYPE_PLUGIN,
  PROCESS_TYPE_WORKER,
  PROCESS_TYPE_NACL,
  PROCESS_TYPE_SERVICE_WORKER,
  PROCESS_TYPE_UTILITY,
  PROCESS_TYPE_GPU,
  PROCESS_TYPE_OTHER,
  PROCESS_TYPE_LAST = PROCESS_TYPE_OTHER,
};


struct TaskInfo {
  TaskInfo();
  ~TaskInfo();
  TaskInfo(TaskInfo&& rhs);
 
  //task_id
  std::string task_id;

  // The title of the task.
  std::string title;

  // Optional tab ID, if this task represents a tab running on a renderer process.
  std::unique_ptr<int> tab_id;

  double cpu;

 private:
  DISALLOW_COPY_AND_ASSIGN(TaskInfo);
};

struct Cache {
  Cache();
  ~Cache();
  Cache(Cache&& rhs);
 
  // The size of the cache, in bytes.
  double size;

  // The part of the cache that is utilized, in bytes.
  double live_size;


 private:
  DISALLOW_COPY_AND_ASSIGN(Cache);
};

struct Process {
  Process();
  ~Process();
  Process(Process&& rhs);
 

  // Unique ID of the process provided by the browser.
  int id;

  // The ID of the process, as provided by the OS.
  int os_process_id;

  // The type of process.
  ProcessType type;

  // The profile which the process is associated with.
  std::string profile;

  // The debugging port for Native Client processes. Zero for other process types
  // and for NaCl processes that do not have debugging enabled.
  int nacl_debug_port;

  // Array of TaskInfos representing the tasks running on this process.
  std::vector<TaskInfo> tasks;

  // The most recent measurement of the process’s CPU usage, expressed as the
  // percentage of a single CPU core used in total, by all of the process’s
  // threads. This gives a value from zero to CpuInfo.numOfProcessors*100, which
  // can exceed 100% in multi-threaded processes. Only available when receiving
  // the object as part of a callback from onUpdated or onUpdatedWithMemory.
  double cpu;

  // The most recent measurement of the process network usage, in bytes per
  // second. Only available when receiving the object as part of a callback from
  // onUpdated or onUpdatedWithMemory.
  double network;

  // The most recent measurement of the process private memory usage, in bytes.
  // Only available when receiving the object as part of a callback from
  // onUpdatedWithMemory or getProcessInfo with the includeMemory flag.
  double private_memory;

  // The most recent measurement of the process JavaScript allocated memory, in
  // bytes. Only available when receiving the object as part of a callback from
  // onUpdated or onUpdatedWithMemory.
  double js_memory_allocated;

  // The most recent measurement of the process JavaScript memory used, in bytes.
  // Only available when receiving the object as part of a callback from onUpdated
  // or onUpdatedWithMemory.
  double js_memory_used;

  // The most recent measurement of the process’s SQLite memory usage, in bytes.
  // Only available when receiving the object as part of a callback from onUpdated
  // or onUpdatedWithMemory.
  std::unique_ptr<double> sqlite_memory;

  // The most recent information about the image cache for the process. Only
  // available when receiving the object as part of a callback from onUpdated or
  // onUpdatedWithMemory.
  std::unique_ptr<Cache> image_cache;

  // The most recent information about the script cache for the process. Only
  // available when receiving the object as part of a callback from onUpdated or
  // onUpdatedWithMemory.
  std::unique_ptr<Cache> script_cache;

  // The most recent information about the CSS cache for the process. Only
  // available when receiving the object as part of a callback from onUpdated or
  // onUpdatedWithMemory.
  std::unique_ptr<Cache> css_cache;


 private:
  DISALLOW_COPY_AND_ASSIGN(Process);
};

// Observes the Task Manager and routes the notifications as events to the
// extension system.
class SWProcessesForensics : public task_manager::TaskManagerObserver {
 public:
  SWProcessesForensics();
   
  ~SWProcessesForensics() override;
  
  void DummyMethod(){}
  // task_manager::TaskManagerObserver:
  void OnTaskAdded(task_manager::TaskId id) override;
  void OnTaskToBeRemoved(task_manager::TaskId id) override;
  void OnTasksRefreshed(const task_manager::TaskIdList& task_ids) override {}
  void OnTasksRefreshedWithBackgroundCalculations(
      const task_manager::TaskIdList& task_ids) override;
  void OnTaskUnresponsive(task_manager::TaskId id) override;

  
//   DISALLOW_COPY_AND_ASSIGN(SWProcessesForensics);
};


}  // namespace sw_forensics

#endif  // CHROME_BROWSER_SW_PROCESSES_FORENSICS_H__
