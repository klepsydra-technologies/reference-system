
folder_with_current_csv='/home/kpsruser/colcon_ws/src/genetic_optimizer/csv_out/'
best_policy_json='/home/kpsruser/kpe-ros2-core/tests/config/best_policy.json'
folder_policy_output='/home/kpsruser/kpe-ros2-core/tests/config/'
exported_json_file='/home/kpsruser/kpe-ros2-core/tests/config/exported.json'
python3 demo_genetic_optimizer.py -i ${exported_json_file} -c ${folder_with_current_csv} \
    -p ${folder_policy_output} -o ${folder_policy_output}