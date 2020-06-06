import keras
import pymysql 
import os
import numpy as np 

from model import  *


from PIL import Image

from sklearn.model_selection import train_test_split




class PyMysql():
    def __init__ (self, host="127.0.0.1", user="root", password="192218", db="minist"):
        self.connection = pymysql.connect(host=host,
        user=user,
        password=password,
        db=db)
    def AcquireData(self):
        cur = self.connection.cursor()
        sql = "SELECT * FROM test1"
        cur . execute(sql)
        data = cur.fetchall()
        self.connection.commit()
        self.connection.close()
        print(data)
        return data

    def CreatTable(self,tableName="hello",size=20):
        cur = self.connection.cursor()
        
        tempCmd =  "CREATE TABLE " + tableName + "(lable INT NOT NULL, picdata BLOB,datasize INT)"
        print(tempCmd)
        cur.execute(tempCmd)

        self.connection.commit()
        self.connection.close()


    def DelTable(self,tableName):
        cur = self.connection.cursor()
   
        tempCmd =  "DROP TABLE " +tableName
        #print(tempCmd)
        cur.execute(tempCmd)
        print("del commit!")
        self.connection.commit()
        self.connection.close() 


    def InsertData2Table(self,filePath ="NULL",tableName ="NULL",size=20):

        picDirs = os.listdir(filePath)
        cur = self.connection.cursor()
        

        for picdir in  picDirs:
            lable  = picdir
            print(lable)
            picdirs = filePath+picdir+'/'
            print(picdirs)
            piclist=os.listdir(picdirs)  # get lable's dir 
            #print(len(piclist))    
            for pic in piclist:
                oldPath=picdirs+pic   # pic dir
                fp = open(oldPath, 'rb')
                img = fp.read()
                fp.close()
                sql = "INSERT INTO test1 VALUES  (%s, %s, %s);"
                args = (lable,img,str(size))
                cur.execute(sql, args)

        self.connection.commit()
        self.connection.close()

    def  DrawData2Numpy(self,tableName ="NULL",size=20):
        cur = self.connection.cursor()
        X =[]
        Y =[]

        try:
        # 执行SQL语句
            cur.execute("SELECT * FROM test1 ")
            
        # 获取所有记录列表
            results = cur.fetchall()
            for row in results:
                fout = open('test_new.jpg', 'wb')
                lable = row[0]
                pic = row[1]
                size = row[2]
                fout.write(pic)
                fout.close()
                img = np.array(Image.open("./test_new.jpg"))
                print(img)
                X.append(img)
                Y.append(lable)

        
        
                # 打印结果
                #print("fname=%s,lname=%s,age=%s",(lable, pic, size))
        except:
            print ("Error: unable to fetch data")

        np.save("data.npy", X)
        np.save("lable.npy", Y)
        self.connection.commit()
        self.connection.close()

    
    def ChoseModel(self,name="simple_CNN",optimizers="adam",validation_splits=0.1,epoch=10 ,batch=64,saveModel=False,size=20):
        
        input_shape = (size, size, 1)

        batch_size = batch


        num_epochs = epoch

        validation_split = validation_splits

        base_path = './models/'


        X = np.load("data.npy",allow_pickle = True)
        y = np.load("lable.npy",allow_pickle = True)
        num_classes = np.max(y)+1
        print(num_classes)

        print(X.shape)
        print(y.shape)
        X = X.reshape(X.shape[0],size , size, 1)


        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=validation_split, random_state=10,
                                                            shuffle=True)
        x_train = x_train.reshape(x_train.shape[0], size, size, 1)
        x_test = x_test.reshape(x_test.shape[0], size, size, 1)
        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')
        x_train /= 255
        x_test /= 255
        print('x_train shape:', x_train.shape)
        print(x_train.shape[0], 'train samples')
        print(x_test.shape[0], 'test samples')
        y_train = keras.utils.to_categorical(y_train, num_classes)
        y_test = keras.utils.to_categorical(y_test, num_classes)


        
        if name =="simple_CNN":
            model = simple_CNN(input_shape, num_classes)

        model.compile(optimizer=optimizers, # 优化器采用adam
                    loss='categorical_crossentropy', # 多分类的对数损失函数
                    metrics=['accuracy'])
        model.summary()

        history =model.fit(x_train, y_train,
                batch_size=batch_size,
                epochs=num_epochs,
                verbose=1,
                validation_data=(x_test, y_test),)
        

        if saveModel==True:
            model.save(base_path+'cnn2.h5')
        




if __name__ == "__main__":
    test = PyMysql()
    #test.AcquireData()
    #test.DelTable("test")
    #test.CreatTable("test",20)
    
    #test.InsertData2Table("./filedata/",'test',20)
    #test.DrawData2Numpy('test1',20)
    test.ChoseModel("simple_CNN","adam",0.1,50,64,True,20)








