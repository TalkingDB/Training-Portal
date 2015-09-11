<html>
    <head>
        <meta charset="UTF-8">
        <title></title>
    </head>
    <body>
        <div style="width: 80%;padding: 50px;">
            <?php
//        Display Php Errors
            ini_set('display_startup_errors', 1);
            ini_set('display_errors', 1);
            error_reporting(-1);
            ini_set('max_execution_time', 0);

//          Make Connection with Mongo Db
            $connection = new MongoClient('target-ricky.smarter.codes');
            $db = $connection->noisy_NER;

            if (isset($_GET['user']) && $_GET['user'] != "") {
                $user = $_GET['user'];
                if (isset($_POST['submit'])) {
                    saveEntityUrl($db, $user);
                }
            } else {
                echo '<h5>***** No User Found. Please Specify the user in Url. ******</h5>';
            }



//            $collection = $db->entity;
//            $entity_relation = $db->entity_relation;
//            
//            
//            $cursor = $collection->find(array("entity_url" => new MongoRegex("/>clothing$/i")));;
//            foreach ($cursor as $document) {
//                pr($document);
//                $collection->remove(array('_id' => $document['_id']));
//            }
//            
//            
//            $cursor = $entity_relation->find();
//            foreach ($cursor as $document) {
//                pr($document);
//                $entity_relation->remove(array('_id' => $document['_id']));
//            }
//            
//            
//            $db->collection->insert($content);
//            $newDocID = $content['_id'];
//            db.entity.find({"intended_trainer": "Target_trainer"}).forEach( function(e) { e.entity_url = e.entity_url.toLowerCase();
//             db.entity.save(e);
//            } )
            ?> 

            <h2>Bulk data entry of relations ></h2>
            <h4>* Enter Each Entity in New Line</h4>
            <h4>* Multiple Entities can be entered For one Textarea at a Time</h4>
            <form method="post">
                <table border="1px">
                    <tr>
                        <th>Left Side Entity Url</th>
                        <th>Relation</th>
                        <th>Right Side Entity Url</th>
                    </tr>
                    <tr>
                        <td><textarea  name="left_side_entity_url" rows="5" cols="35"></textarea>
                            <br><br> Part Of Speech : 
                            <input type="text" name="left_speech" value="common" style="width: 170px;" />
                        </td>
                        <td>
                            <select name="relation">
                                <option value="isHyponymOf">Is Hyponym Of</option>
                                <option value="isMeronymOf">Is Meronym Of</option>
                                <!--<option value="hasSynonym">Has Synonym</option>-->
                            </select>
                        </td>
                        <td> <textarea name="right_side_entity_url" rows="5" cols="35"></textarea>
                            <br><br> Part Of Speech : 
                            <input type="text" name="right_speech" value="common" style="width: 200px;" />
                        </td>
                    </tr>
                    <tr>
                        <td colspan="3">
                            <input type="submit" name="submit" value="submit" style="height: 30px; width: 120px;" />
                        </td>
                    </tr>
                </table>
            </form>
        </div>



        <!--******************Functions*****************-->
        <?php

        function saveEntityUrl($db, $user) {
            $collection = $db->entity;
            $entity_relation = $db->entity_relation;
            $valid = validate($_POST);
            if ($valid) {

                $left_side_entity_url = $_POST['left_side_entity_url'];
                $right_side_entity_url = $_POST['right_side_entity_url'];
                $relation = $_POST['relation'];
                $part_of_speech_left = $_POST['left_speech'];
                $part_of_speech_right = $_POST['right_speech'];

                if (strstr($left_side_entity_url, "\n")) {
                    $entities_relation = explode("\n", $left_side_entity_url);
                    $entities = $entities_relation;
                    $entities[] = trim($right_side_entity_url);
                    $part_of_speech = $part_of_speech_left;
                    $object = $right_side_entity_url;
                } else if (strstr($right_side_entity_url, "\n")) {
                    $entities_relation = explode("\n", $right_side_entity_url);
                    $entities = $entities_relation;
                    $entities[] = trim($left_side_entity_url);
                    $part_of_speech = $part_of_speech_right;
                    $object = $left_side_entity_url;
                } else {
                    $entities_relation = array($left_side_entity_url);
                    $entities = $entities_relation;
                    $entities[] = trim($right_side_entity_url);
                    $part_of_speech = $part_of_speech_left;
                    $object = $right_side_entity_url;
                }



//                if (strstr($object, " ")) {
//                    $object = str_replace($object, " ", "_");
//                }
//                $object = strtolower($object);

                $entity_url_array = array();
                $to_insert_entity_array = returnToInsertValues($entities, $db, $entity_url_array);
                $to_insert_entity_relation_array = returnToInsertRelationValues($entities_relation, $relation, $object, $db, $entity_url_array);

                if (!empty($to_insert_entity_array)) {
                    foreach ($to_insert_entity_array as $entity => $value) {
                        if ($value == 1) {
                            if (trim($entity_url_array[trim($entity)]) != "") {
                                $entity_array = array(
                                    "entity_url" => trim($entity_url_array[trim($entity)]),
                                    "surface_text" => trim(strtolower($entity)),
                                    "how_this_record" => "Bulk data entry",
                                    "entity_part_of_speech" => trim($part_of_speech),
                                    "intended_trainer" => "Target_trainer",
                                    "user" => $user
                                );

                                deleteEntity($db, trim($entity));
                                if ($collection->insert($entity_array)) {
                                    echo 'Successfully Inserted Entity ' . $entity . '<br>';
                                } else {
                                    echo 'Failed  Inserting Entity Relation ' . $entity . '<br>';
                                }
                            }
                        } else {
                            echo 'Already Exists in DB ' . $entity . '<br>';
                        }
                    }
                }

                if (!empty($to_insert_entity_relation_array)) {
                    foreach ($to_insert_entity_relation_array as $entity => $value) {
                        if ($value == 1) {
                            if ($entity_url_array[trim($entity)] != "") {
                                $entity_relation_array = array(
                                    "subject" => trim($entity_url_array[trim($entity)]),
                                    "relation" => $relation,
                                    "object" => trim($entity_url_array[trim($object)])
                                );

                                if ($entity_relation->insert($entity_relation_array)) {
                                    echo 'Successfully Inserted Entity Relation ' . $entity . '<br>';
                                } else {
                                    echo 'Failed  Inserting Entity Relation ' . $entity . '<br>';
                                }
                            }
                        } else {
                            echo 'Already Exists in DB ' . $entity . '<br>';
                        }
                    }
                }

                return TRUE;
            } else {
                return FALSE;
            }
        }

        function deleteEntity($db, $entity) {
            $collection = $db->entity;
            $cursor = $collection->find(array("surface_text" => new MongoRegex("/^$entity$/i")));
            foreach ($cursor as $document) {
                $collection->remove(array('_id' => $document['_id']));
            }
        }

        function returnToInsertValues($entities, $db, &$entity_url_array) {
            $collection = $db->entity;
            $to_insert_array = array();
            foreach ($entities as $entity) {
                $to_insert_array[trim($entity)] = 1;
                if (strstr($entity, " ")) {
                    $string = str_replace(" ", "_", $entity);
                } else {
                    $string = $entity;
                }
                $var = trim($string);
                $cursor = $collection->find(array("entity_url" => new MongoRegex("/>$var$/i")));
                $entity_url_array[trim($entity)] = "SmarterCodes>" . trim($var);

                foreach ($cursor as $obj) {
                    if (!empty($obj)) {
                        $to_insert_array[trim($entity)] = 0;
                        $entity_url_array[trim($entity)] = $obj['entity_url'];
                    }
                }
            }

            return $to_insert_array;
        }

        function returnToInsertRelationValues($entities, $relation, $object, $db, $entity_url_array) {
            $entity_relation = $db->entity_relation;
            $to_insert_array = array();
            foreach ($entities as $entity) {
                $to_insert_array[trim($entity)] = 1;
                $var = $entity_url_array[trim($entity)];
                $object_with_prefix = $entity_url_array[trim($object)];

                $cursor = $entity_relation->find(array("subject" => $var, "object" => $object_with_prefix, "relation" => $relation));
                foreach ($cursor as $obj) {
                    if (!empty($obj)) {
                        $to_insert_array[trim($entity)] = 0;
                    }
                }
            }
            return $to_insert_array;
        }

        function validate($array) {

            $left_side_entity_url = $array['left_side_entity_url'];
            $right_side_entity_url = $array['right_side_entity_url'];
            $relation = $array['relation'];
            $part_of_speech_left = $array['left_speech'];
            $part_of_speech_right = $array['right_speech'];

            if ($left_side_entity_url != "" && $relation != "" && $right_side_entity_url != "") {
                if ($relation != "" && $relation == 'hasSynonym') {
                    if (strstr(trim($left_side_entity_url), "\n")) {
                        echo '<h5>***** For Synonym Only one entity for Left Side ******</h5>';
                        return FALSE;
                    }
                    return TRUE;
                } else {
                    $exist = 0;
                    if (strstr($left_side_entity_url, "\n")) {
                        $exist = 1;
                        if (trim($part_of_speech_left) == "") {
                            echo '<h5>*****Left Part of Speech Can not be Empty ******</h5>';
                            return FALSE;
                        }
                    }

                    if (strstr($right_side_entity_url, "\n") && $exist == 1) {
                        echo '<h5>*****Multiple Entities can be entered For one Textarea******</h5>';
                        return FALSE;
                    } else {
                        if (trim($part_of_speech_right) == "") {
                            echo '<h5>*****Right Part of Speech Can not be Empty ******</h5>';
                            return FALSE;
                        }
                    }
                    return TRUE;
                }
            } else {
                echo '<h5>***** All Feilds are Mandatory ******</h5>';
            }
            return FALSE;
        }

        function pr($array) {
            echo '<pre>';
            print_r($array);
            echo '</pre>';
        }
        ?>

        <style>
            table{
                height: 300px; 
                text-align: center; 
                width: 95%;
            }

            textarea {
                resize: none;
            }
        </style>

    </body>
</html>


