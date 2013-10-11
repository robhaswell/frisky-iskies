<?php
/**
 * Zend Framework (http://framework.zend.com/)
 *
 * @link      http://github.com/zendframework/ZendSkeletonApplication for the canonical source repository
 * @copyright Copyright (c) 2005-2013 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */

namespace Application\Controller;

use Zend\Mvc\Controller\AbstractActionController;
use Zend\View\Model\ViewModel;

class IndexController extends AbstractActionController
{
    public function indexAction()
    {
        /* TODO: Develop this with an internet connection so I can read the
           documentation. */
        if (@$_POST['action'] == "data")
            return $this->dataAction();
        $db = $this->getAdapter();
        $items = $db->query("select id, name, `group`,
            (sell_med-buy_med)/buy_med*100 as margin from items where volume >
            10000 having margin > 10 order by profit desc limit
            100")->execute();
        return new ViewModel(Array(
            'items' => $items,
        ));
    }

    public function dataAction() {
        // TODO: Don't access this array directly.
        $id = $_POST['id'];
        $db = $this->getAdapter();
        $items = $db->query("select * from price_history where item_id=? and
            timestamp >= date_sub(now(), interval 10
            day)")->execute(Array($id));
        // TODO: Output this as JSON in a nicer fashion.
        $data = Array();
        foreach ($items as $row)
            $data[] = $row;
        echo json_encode($data); die;
    }

    public function getAdapter()
    {
        if (!isset($this->adapter) or !$this->adapter) {
            $sm = $this->getServiceLocator();
            $this->adapter = $sm->get('Zend\Db\Adapter\Adapter');
        }
        return $this->adapter;
    }
}
